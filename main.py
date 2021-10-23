from flask import Flask, send_from_directory

app = Flask(__name__)

@app.route('/')
def index():
    return 'Index Page'

@app.route('/hello')
def hello():
    return send_from_directory("front_end", "homepage.html")
    # return "Hello world"
