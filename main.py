from flask import Flask,jsonify,request
import os
import google_auth
from pymongo import MongoClient
from bson.objectid import ObjectId
import bson
import certifi 



app = Flask(__name__)
app.secret_key = os.environ.get('_FLASK_SECRET_KEY')
app.register_blueprint(google_auth.app)
MONGO_URL = os.environ.get('_MONGO_URL_')
DB_NAME = os.environ.get('_DB_NAME_')

client = MongoClient(MONGO_URL, tlsCAFile=certifi.where())
db = client[DB_NAME]
collection = db["tasks"]




#add todo
@app.route('/todo/add', methods = ['POST']) 
def add_a_task():
    token = google_auth.get_token()
    isValidToken = google_auth.verify_token(token)
    if isValidToken:
        user_email = google_auth.get_user_email(token)
        req = request.get_json(force=True)
        task = req["task"]
        collection.insert_one({'task': task, 'completed': False, 'user_email': user_email})
        return jsonify({'status': True, 'message': 'task added successfully'}),201
    return google_auth.unauthenticated()


#get all Tasks, Auth User 
@app.route('/todo/tasks', methods = ['GET']) 
def get_all_tasks():
    token = google_auth.get_token()
    isValidToken = google_auth.verify_token(token)
    if isValidToken:
        user_email = google_auth.get_user_email(token)
        data = []
        for doc in collection.find({"user_email": {"$eq": user_email }}):
            doc['_id'] = str(doc['_id']) 
            data.append(doc)
        if len(data):
            return jsonify(data)
        else:
            return jsonify({})    
    return google_auth.unauthenticated()


#update todo 
@app.route('/todo/update/<id>', methods = ['PATCH']) 
def update_a_task(id):
    token = google_auth.get_token()
    isValidToken = google_auth.verify_token(token)
    if isValidToken:
        responseMsg ={'status': False, 'message': 'Invalid todo id is supplied'}
        try:
            todo = collection.find_one({'_id': ObjectId(id)})
            have_list = True if len(list(todo)) else False;
            if have_list:
                collection.update_one({'_id': ObjectId(id)}, {'$set': {'completed': True}})
                return jsonify({'status': True, 'message': 'updated'})
        except bson.errors.InvalidId:
            return jsonify(responseMsg)
        except TypeError: 
            return jsonify(responseMsg) 
    return google_auth.unauthenticated()

#delete todo
@app.route('/todo/delete/<id>', methods = ['DELETE'])
def delete_a_task(id):
    token = google_auth.get_token()
    isValidToken = google_auth.verify_token(token)
    if isValidToken:
        responseMsg ={'status': False, 'message': 'Invalid todo id is supplied'}
        try:
            todo = collection.find_one({'_id': ObjectId(id)})
            have_list = True if len(list(todo)) else False;
            if have_list:
                collection.delete_one({'_id': ObjectId(id)})
                return jsonify({'status': True, 'message': 'deleted'})
        except bson.errors.InvalidId:
            return jsonify(responseMsg)
        except TypeError: 
            return jsonify(responseMsg) 
    return google_auth.unauthenticated()         

