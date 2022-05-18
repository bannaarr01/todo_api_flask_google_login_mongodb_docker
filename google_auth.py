import functools
import os
import flask
from flask import jsonify,request
from authlib.client import OAuth2Session
import google.oauth2.credentials
import googleapiclient.discovery

#verify token
from google.oauth2 import id_token
from google.auth.transport import requests


AUTH_ACCESS_TOKEN_URL = 'https://www.googleapis.com/oauth2/v4/token'
AUTH_URL = 'https://accounts.google.com/o/oauth2/v2/auth?access_type=offline&prompt=consent'
AUTH_SCOPE ='openid email profile'
TOKEN_REVOKE_URL = 'https://accounts.google.com/o/oauth2/revoke?token='

AUTH_CALLBACK_URL = os.environ.get("_AUTH_CALLBACK_URL", default=False)
BASE_URL = os.environ.get("_BASE_URL", default=False)
CLIENT_ID = os.environ.get("_CLIENT_ID", default=False)
CLIENT_SECRET = os.environ.get("_CLIENT_SECRET", default=False)

AUTH_TOKEN_KEY = 'auth_token'
AUTH_STATE_KEY = 'auth_state'

app = flask.Blueprint('google_auth', __name__)


#if not authenticated
def unauthenticated():
    responseMsg = {
        "status": False,
        "message": "Unauthenticated"
    }
    return jsonify(responseMsg)


def no_cache(view):
    @functools.wraps(view)
    def no_cache_impl(*args, **kwargs):
        response = flask.make_response(view(*args, **kwargs))
        response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '-1'
        return response

    return functools.update_wrapper(no_cache_impl, view)


#login
@app.route('/google/login')
@no_cache
def login():
    session = OAuth2Session(CLIENT_ID, CLIENT_SECRET,
                            scope=AUTH_SCOPE,
                            redirect_uri=AUTH_CALLBACK_URL)
  
    url, state = session.authorization_url(AUTH_URL)

    flask.session[AUTH_STATE_KEY] = state
    flask.session.permanent = True

    return flask.redirect(url, code=302)


@app.route('/google/auth')
@no_cache
def google_auth_redirect():
    req_state = flask.request.args.get('state', default=None, type=None)

    if req_state != flask.session[AUTH_STATE_KEY]:
        response = flask.make_response(jsonify({'status':False,'message':'Invalid state parameter'}), 401)
        return response
    
    session = OAuth2Session(CLIENT_ID, CLIENT_SECRET,
                            scope=AUTH_SCOPE,
                            state=flask.session[AUTH_STATE_KEY],
                            redirect_uri=AUTH_CALLBACK_URL)
    oauth2_tokens = session.fetch_access_token(
                        AUTH_ACCESS_TOKEN_URL,            
                        authorization_response=flask.request.url)
    flask.session[AUTH_TOKEN_KEY] = oauth2_tokens
    return jsonify(flask.session)


#get Token
def get_token():
    hasAuthHeader = 'Authorization' in request.headers
    if hasAuthHeader:
        try:
            bearer = request.headers.get('Authorization')
            token = bearer.split()[1]
            return token
        except: #if indexOutOfRange when Bearer and token not well supplied
            return ''
    return '' #if request has no Authorization header


#verify token
def verify_token(token):
    try:
        # import pdb; pdb.set_trace()
        id_token.verify_oauth2_token(token, requests.Request(), CLIENT_ID)
        return True
    except ValueError: #if token is Invalid
        return False

def get_user_email(token):
    user = id_token.verify_oauth2_token(token, requests.Request(), CLIENT_ID)
    return user['email']


# @app.route('/logout', methods=['POST'])
# def logout(): 
#     token = get_token() #refresh token
#     return flask.redirect(f'{TOKEN_REVOKE_URL}{token}', code=302) 
# #to Revoke 
    


    