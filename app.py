import os 
from test import foundry_token

os.environ['FOUNDRY_TOKEN'] = foundry_token
from flask import Flask, render_template, url_for, redirect, request
from object_to_orbit import make_orbits

app = Flask(__name__)
app.config['SECRET_KEY'] = 'Jg%&o(,/jn>?KM4dUGJ12341scx)'

@app.route('/', methods=['GET', 'POST'])
def index():
    objectsStr = request.args.get('objects')
    if objectsStr:
        objects = objectsStr.split(',')
        make_orbits(objects)
    return render_template("index.html")

@app.route('/addOrbit', methods=['GET'])
def addOrbit():
    return render_template("hello world")

# RUN APP
if __name__ == '__main__':
    app.run(debug=True, port=8000)