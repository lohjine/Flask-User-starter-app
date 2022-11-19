import flask
from flask import flash
from flask_login import current_user, login_user
from flask_dance.contrib.google import make_google_blueprint
from flask_dance.consumer import oauth_authorized, oauth_error
from flask_dance.consumer.storage.sqla import SQLAlchemyStorage
from sqlalchemy.orm.exc import NoResultFound
from app import db
from app.models.user_models import User, OAuth
from flask import redirect, url_for
import json

blueprint = make_google_blueprint(
    scope=["profile", "email"],
    storage=SQLAlchemyStorage(OAuth, db.session, user=current_user),
)


# create/login local user on successful OAuth login
@oauth_authorized.connect_via(blueprint)
def google_logged_in(blueprint, token):
    if not token:
        flash("Failed to log in with Google.", category="danger")
        return False

    resp = blueprint.session.get("/oauth2/v2/userinfo")
    if not resp.ok:
        msg = "Failed to fetch user info from Google."
        flash(msg, category="error")
        return False

    google_info = resp.json()
    google_user_id = str(google_info["id"])

    # Find this OAuth token in the database, or create it
    query = OAuth.query.filter_by(
        provider=blueprint.name, provider_user_id=google_user_id
    )
    try:
        oauth = query.one()
    except NoResultFound:
        google_user_login = str(google_info["email"])
        oauth = OAuth(
            provider=blueprint.name,
            provider_user_id=google_user_id,
            provider_user_login=google_user_login,
            provider_data=json.dumps(google_info),
            token=token,
        )

    # Now, figure out what to do with this token. There are 2x2 options:
    # user login state and token link state.
    if current_user.is_anonymous:
        if oauth.user:
            if not oauth.user.active:
                flash('Your account is disabled.', 'error')
                return redirect(url_for('user.login'))
            # If the user is not logged in and the token is linked,
            # log the user into the linked user account
            login_user(oauth.user)
            flash("Successfully signed in with Google.", "success")
            # retrieve `next_url` from Flask's session cookie
            next_url = flask.session.get("next_url","/")
            if next_url != "/":
                flask.session.pop("next_url")
            # redirect the user to `next_url`
            return flask.redirect(next_url)
        else:
            # If the user is not logged in and the token is unlinked,
            # create a new local user account and log that account in.
            # This means that one person can make multiple accounts, but it's
            # OK because they can merge those accounts later.
            user = User(active = True)
            oauth.user = user
            db.session.add_all([user, oauth])
            db.session.commit()
            login_user(user)
            flash("Successfully signed in with Google.", "success")
            # retrieve `next_url` from Flask's session cookie
            next_url = flask.session.get("next_url","/")
            if next_url != "/":
                flask.session.pop("next_url")
            # redirect the user to `next_url`
            return flask.redirect(next_url)
    else:
        if oauth.user:
            # If the user is logged in and the token is linked, check if these
            # accounts are the same!
            if current_user != oauth.user:
#                # Account collision! Ask user if they want to merge accounts.
#                url = url_for("auth.merge", username=oauth.user.username)
#                return redirect(url)
#                flash("Successfully linked Google account.", "success")
                flash(f"""The Google account ({str(google_info["email"])}) has already been used to link to another account here.<br>
                      If you would like to access that account, sign out of this account and log in using Google.""", "error")
                return redirect(url_for('main.user_profile_page'))
        else:
            # If the user is logged in and the token is unlinked,
            # link the token to the current user
            oauth.user = current_user
            db.session.add(oauth)
            db.session.commit()
            flash("Successfully linked Google account.", "success")
            return redirect(url_for('main.user_profile_page'))

    # Indicate that the backend shouldn't manage creating the OAuth object
    # in the database, since we've already done so!
    return False


# notify on OAuth provider error
@oauth_error.connect_via(blueprint)
def google_error(blueprint, message, response):
    msg = ("OAuth error from {name}! " "message={message} response={response}").format(
        name=blueprint.name, message=message, response=response
    )
    flash(msg, category="error")
