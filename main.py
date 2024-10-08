import json
from os import environ as env
from urllib.parse import quote_plus, urlencode

from functools import wraps
from authlib.integrations.flask_client import OAuth
from dotenv import find_dotenv, load_dotenv
from flask import Flask, redirect, render_template, session, url_for


app = Flask(__name__)
app.secret_key = env.get("APP_SECRET_KEY")

oauth = OAuth(app)

oauth.register(
    "auth0",
    client_id=env.get("AUTH0_CLIENT_ID"),
    client_secret=env.get("AUTH0_CLIENT_SECRET"),
    client_kwargs={
        "scope": "openid profile email",
    },
    server_metadata_url=f'https://{env.get("AUTH0_DOMAIN")}/.well-known/openid-configuration',
)

@app.route("/")
def home():
    return render_template("main.html", session=session.get('user'), pretty=json.dumps(session.get('user'), indent=4))

@app.route('/hi', methods=['GET'])
def main():
    print(request.headers)
    user_name = request.args.get("userName", "unknown")
    return render_template('main.html', user=user_name)

@app.route("/login")
def login():
    return oauth.auth0.authorize_redirect(
        redirect_uri=url_for("callback", _external=True)
    )

@app.route("/callback", methods =["GET", "POST"])
def callback():
    token = oauth.auth0.authorize_access_token()
    session["user"] = token
    return redirect("/")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(
        "https://" + env.get("AUTH0_DOMAIN")
        + "/v2/logout?"
        + urlencode(
            {
                "returnTo": url_for("home", _external=True),
                "client_id": env.get("AUTH0_CLIENT_ID"),
            },
            quote_via=quote_plus,
        )
    )



def requires_auth(f):
  @wraps(f)
  def decorated(*args, **kwargs):
    if 'user' not in session:
      # Redirect to Login page here
      return redirect('/')
    return f(*args, **kwargs) #do the normal behavior -- return as it does.

  return decorated


@app.route('/secret', methods=['GET'])
@requires_auth
def render_secret():
    return render_template("secret.html")