from flask import Flask, jsonify,url_for
import os
import google_auth
from pymongo import MongoClient
import certifi 

app = Flask(__name__)
app.secret_key = os.environ.get('_FLASK_SECRET_KEY')
app.register_blueprint(google_auth.app)
MONGO_URL = os.environ.get('_MONGO_URL_')
DB_NAME = os.environ.get('_DB_NAME_')

client = MongoClient(MONGO_URL, tlsCAFile=certifi.where())
db = client[DB_NAME]
collection = db["tasks"]

#get all Tasks, Auth User Only
@app.route('/todo/tasks', methods = ['GET']) 
def main():
    if google_auth.is_logged_in():
        data = []
        for doc in collection.find():
            doc['_id'] = str(doc['_id']) 
            data.append(doc)
        return jsonify(data)
    return google_auth.unauthenticated()

