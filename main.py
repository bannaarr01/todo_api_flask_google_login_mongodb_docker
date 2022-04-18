from flask import Flask, jsonify
import os
import google_auth

app = Flask(__name__)
app.secret_key = os.environ.get('_FLASK_SECRET_KEY')
app.register_blueprint(google_auth.app)

