from flask import Flask, g
from pymongo import MongoClient
from flask_cors import CORS, cross_origin
import os
import json

app = Flask(__name__)
CORS(app)


@app.route("/data")
def data():
    client = get_db()
    db = client.get_default_database()
    return json.dumps(db.data.find_one()['data'])


def get_db():
    """Opens a new database connection if there is none yet for the
    current application context.
    """
    if not hasattr(g, 'mongo_db'):
        g.mongo_db = MongoClient(os.environ["MONGODB_URI"])
    return g.mongo_db


@app.teardown_appcontext
def close_db(error):
    """Closes the database again at the end of the request."""
    if hasattr(g, 'mongo_db'):
        g.mongo_db.close()


@app.route('/')
def hello_world():
    return 'Hello, World!'
