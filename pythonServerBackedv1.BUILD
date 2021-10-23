from flask import request
from flask import Flask
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)
logins = []
open_rides = []

@app.route("/")
def hello_world():
    return send_from_directory("front_end", "home.html")
  
@app.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        error = None
        user = db.execute(
            'SELECT * FROM user WHERE username = ?', (username,)
        ).fetchone()

        if user is None:
            error = 'Incorrect username.'
        elif not check_password_hash(user['password'], password):
            error = 'Incorrect password.'

        if error is None:
            session.clear()
            session['user_id'] = user['id']
            return redirect(url_for('index'))

        flash(error)

    return send_from_directory("front_end", "login.html")

@app.route('/register', methods=["POST"])
def hello():
  	if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        inserted = insert_user(username, generate_password_hash(password))
        
            
        
        return redirect(url_for("login"))

    else:
        return send_from_directory("front_end", "login.html")
  
def find_user(username, hash_password):
	xx = username,hash_password
  if xx in logins:
    return True
  else:
    return False

  def insert_user(username, hash_password):
  x = find_user(username, hash_password)
  if x == True:
    return False
  else:
    logins.append((username,hash_password))
    return True
  
  
  
  
