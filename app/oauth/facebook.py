from flask import flash
from flask_login import current_user
from flask_dance.contrib.facebook import make_facebook_blueprint
from flask_dance.consumer import oauth_authorized, oauth_error
from flask_dance.consumer.storage.sqla import SQLAlchemyStorage
from app import db
from app.models.user_models import OAuth
from app.oauth.utils import handle_oauth_authorized

blueprint = make_facebook_blueprint(
    storage=SQLAlchemyStorage(OAuth, db.session, user=current_user),
)


# create/login local user on successful OAuth login
@oauth_authorized.connect_via(blueprint)
def facebook_logged_in(blueprint, token):
    if not token:
        flash("Failed to log in with Facebook.", category="danger")
        return False

    resp = blueprint.session.get("/me")
    if not resp.ok:
        msg = "Failed to fetch user info from Facebook."
        flash(msg, category="error")
        return False

    facebook_info = resp.json()
    return handle_oauth_authorized(
        blueprint.name,
        token,
        {
            'id': facebook_info['id'],
            'login': facebook_info.get('email') or facebook_info.get('name') or facebook_info['id'],
            'provider_label': 'Facebook',
            'data': facebook_info,
        },
    )


# notify on OAuth provider error
@oauth_error.connect_via(blueprint)
def facebook_error(blueprint, message, response):
    msg = ("OAuth error from {name}! " "message={message} response={response}").format(
        name=blueprint.name, message=message, response=response
    )
    flash(msg, category="error")
