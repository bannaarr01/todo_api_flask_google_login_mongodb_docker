import functools
import os
import flask
from flask import jsonify
from authlib.client import OAuth2Session
import google.oauth2.credentials
import googleapiclient.discovery


AUTH_ACCESS_TOKEN_URL = 'https://www.googleapis.com/oauth2/v4/token'
AUTH_URL = 'https://accounts.google.com/o/oauth2/v2/auth?access_type=offline&prompt=consent'
AUTH_SCOPE ='openid email profile'

AUTH_CALLBACK_URL = os.environ.get("_AUTH_CALLBACK_URL", default=False)
BASE_URL = os.environ.get("_BASE_URL", default=False)
CLIENT_ID = os.environ.get("_CLIENT_ID", default=False)
CLIENT_SECRET = os.environ.get("_CLIENT_SECRET", default=False)

AUTH_TOKEN_KEY = 'auth_token'
AUTH_STATE_KEY = 'auth_state'

app = flask.Blueprint('google_auth', __name__)

#checking if user is logged-in
def is_logged_in():
    return True if AUTH_TOKEN_KEY in flask.session else False

def unauthenticated():
    unauth = {
        "status": False,
        "message": "Unauthenticated"
    }
    return jsonify(unauth)

def build_credentials():
    if not is_logged_in():
        return unauthenticated()
    oauth2_tokens = flask.session[AUTH_TOKEN_KEY]
    return google.oauth2.credentials.Credentials(
                oauth2_tokens['access_token'],
                refresh_token=oauth2_tokens['refresh_token'],
                client_id=CLIENT_ID,
                client_secret=CLIENT_SECRET,
                token_url=AUTH_ACCESS_TOKEN_URL)


#get logged in userInfo
def get_user_info():
    credentials = build_credentials()
    oauth2_client = googleapiclient.discovery.build(
                        'oauth2', 'v2',
                        credentials=credentials)
    return oauth2_client.userinfo().get().execute()


def no_cache(view):
    @functools.wraps(view)
    def no_cache_impl(*args, **kwargs):
        response = flask.make_response(view(*args, **kwargs))
        response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '-1'
        return response

    return functools.update_wrapper(no_cache_impl, view)


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
        response = flask.make_response('Invalid state parameter', 401)
        return response
    
    session = OAuth2Session(CLIENT_ID, CLIENT_SECRET,
                            scope=AUTH_SCOPE,
                            state=flask.session[AUTH_STATE_KEY],
                            redirect_uri=AUTH_CALLBACK_URL)

    oauth2_tokens = session.fetch_access_token(
                        AUTH_ACCESS_TOKEN_URL,            
                        authorization_response=flask.request.url)

    flask.session[AUTH_TOKEN_KEY] = oauth2_tokens

    return flask.redirect(BASE_URL, code=302)