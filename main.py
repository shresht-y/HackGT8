import functools
import uuid
from dataclasses import dataclass
from uuid import uuid4

from flask import Flask, send_from_directory, redirect, url_for, session, g, render_template
from flask import jsonify, request
from flask import json
from werkzeug.security import check_password_hash, generate_password_hash

stop_words = ('your', 'yours', 'yourself', 'yourselves', 'he', 'him', 'his', 'himself', 'she',
              "she's", 'her', 'hers', 'herself', 'it', u"it's", 'its', 'itself', 'they', 'them',
              'their', 'theirs', 'themselves', 'what', 'which', 'who', 'whom', 'this',
              'that', u"that'll", 'these', 'those', 'am', 'is', 'are', 'was', 'were', 'be',
              'been', 'being', 'have', 'has', 'had', 'having', 'do', 'does', 'did', 'doing',
              'a', 'an', 'the', 'and', 'but', 'if', 'or', 'because', 'as', 'until',
              'while', 'of', 'at')


@dataclass
class Ride:
    """Class for keeping track of an item in inventory."""
    eventName: str
    amount_of_people: int
    driver_id: uuid
    rider_id: uuid
    startingLocation: str
    price: float
    ride_id: uuid

    def open(self):
        return self.rider_id is None

    def match_search(self, query):
        tokens = set(query.lower().split()).difference(stop_words)
        event_tokens = set(self.eventName.lower().split()).difference(stop_words)

        for item in tokens:
            if item in event_tokens:
                return True
        return False

    def accepted(self):
        return self.rider_id is not None

    def get_dict(self):
        return {"eventName": self.eventName, "amount_of_people": self.amount_of_people,
                "startingLocation": self.startingLocation, "price": self.price,
                "id": self.ride_id, "accepted": self.accepted()}


@dataclass
class User:
    """Class for keeping track of an item in inventory."""
    email: str
    password_hashed: str
    id: uuid


app = Flask(__name__)
logins = []
open_rides = []
app.secret_key = "58c83446c2d8d97e0389da0d"


def find_user(email, password):
    for person in logins:
        if person.email == email and check_password_hash(person.password_hashed, password):
            return True, person
    else:
        return False, None


def find_user_by_email(email):
    for person in logins:
        if person.email == email:
            return True
    else:
        return False


def insert_user(email, hash_password):
    found = find_user_by_email(email)
    if found:
        return False, None
    else:
        newuser = User(email, hash_password, uuid4())
        logins.append(newuser)
        return True, newuser


def get_user_from_id(user_id):
    for person in logins:
        if person.id == user_id:
            return person
    else:
        return None


def find_ride_with_id(id_of_ride):
    for ride in open_rides:
        if str(ride.ride_id) == id_of_ride:
            return ride
    else:
        return None


def find_driver_ride_with_user_id(user_id):
    return [ride for ride in open_rides if str(ride.driver_id) == str(user_id)]


def find_rider_ride_with_user_id(user_id):
    return [ride for ride in open_rides if str(ride.rider_id) == str(user_id)]


@app.before_request
def load_logged_in_user():
    user_id = session.get('user_id')
    if user_id is None:
        g.user = None
    else:
        g.user = get_user_from_id(user_id)


def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('home'))

        return view(**kwargs)

    return wrapped_view
@app.route("/favicon.ico")
def favicon():
    return send_from_directory('images', "favicon.ico")

@app.route('/images/<path:path>')
def send_js(path):
    return send_from_directory('images', path)


@app.route("/")
def home():
    if g.user:
        return redirect(url_for("main"))
    return send_from_directory("html", "home.html")


@app.route("/main")
@login_required
def main():
    return send_from_directory("html", "main.html")


@app.route('/login', methods=['POST'])
def login():
    if request.method == 'POST':
        email = request.json['email']
        password = request.json['password']

        found, user = find_user(email, password)

        if found:
            session.clear()
            session['user_id'] = user.id
            return jsonify({"redirect": True, "redirect_url": url_for("main")})

        return "Authentication error", 500


@app.route('/register', methods=["POST"])
def register():
    if request.method == 'POST':
        email = request.json['email']
        password = request.json['password']

        inserted, user = insert_user(email, generate_password_hash(password))
        if not inserted:
            return "User already registered", 500

        session.clear()
        session['user_id'] = user.id
        return jsonify({"redirect": True, "redirect_url": url_for("main")})


@app.route('/add_ride', methods=["POST"])
@login_required
def add():
    eventName = request.json["eventName"]
    startingLocation = request.json["startingLocation"]
    price = request.json["price"]
    amountOfPeople = request.json["amountOfPeople"]
    newRide = Ride(eventName=eventName, amount_of_people=amountOfPeople, driver_id=g.user.id,
                   rider_id=None, startingLocation=startingLocation, price=price, ride_id=uuid4())
    open_rides.append(newRide)
    return jsonify(newRide.get_dict())


@app.route('/ride', methods=["GET"])
@login_required
def ride_endpoint():
    ride_id = request.args["id"]
    ride = find_ride_with_id(ride_id)
    if ride is None:
        return "Ride not found", 404
    driver = get_user_from_id(ride.driver_id)
    rider = get_user_from_id(ride.rider_id)
    rider_email = ""
    if rider:
        rider_email = rider.email
    else:
        rider_email = "None"

    return render_template("ride.html", ride=ride, driver_email=driver.email,
                           rider_email=rider_email)


@app.route('/rider_rides', methods=["GET", "FETCH"])
@login_required
def riders_endpoint():
    if request.method == "FETCH":
        user_id = g.user.id
        rider_rides = find_rider_ride_with_user_id(user_id)
        return jsonify([user_ride.get_dict() for user_ride in rider_rides])
    else:
        return send_from_directory("html", "rider.html")


@app.route('/driver_rides', methods=["GET", "FETCH"])
@login_required
def drivers_endpoint():
    if request.method == "FETCH":
        user_id = g.user.id
        driver_rides = find_driver_ride_with_user_id(user_id)
        return jsonify([user_ride.get_dict() for user_ride in driver_rides])
    else:
        return send_from_directory("html", "driver.html")


@app.route('/accept_ride', methods=["POST"])
@login_required
def accept_ride():
    ride_id = request.json["id"]
    accepted_ride = find_ride_with_id(ride_id)
    if accepted_ride is None:
        return "Ride not found", 404
    if accepted_ride.driver_id != g.user.id:
        accepted_ride.rider_id = g.user.id
    else:
        return "Unable to do that", 500
    return json.dumps({'success':True}), 200, {'ContentType':'application/json'}


@app.route('/search', methods=["POST"])
@login_required
def list_rides():
    query = request.json["eventSearch"]
    rides = [candidate_ride.get_dict() for candidate_ride in open_rides if candidate_ride.match_search(query)
             and candidate_ride.rider_id is None]
    return jsonify(rides)


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))


app.run(debug=True)
