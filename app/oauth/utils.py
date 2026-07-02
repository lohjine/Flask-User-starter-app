import json

import flask
from flask import flash, redirect, url_for
from flask_login import current_user, login_user
from sqlalchemy.orm.exc import NoResultFound

from app import db
from app.models.user_models import OAuth, User

OAUTH_PROVIDER_LABELS = {
    'google': 'Google',
    'facebook': 'Facebook',
    'steam': 'Steam',
}

SUPPORTED_PROVIDERS = tuple(OAUTH_PROVIDER_LABELS)


def pop_safe_next_url(default='/'):
    next_url = flask.session.pop('next_url', default)
    return flask.current_app.user_manager.make_safe_url(next_url)


def handle_oauth_authorized(provider_name, token, profile):
    """Create, link, or sign in a local user after provider authorization."""
    provider_user_id = str(profile['id'])
    provider_user_login = str(profile['login'])

    query = OAuth.query.filter_by(
        provider=provider_name,
        provider_user_id=provider_user_id,
    )
    try:
        oauth = query.one()
    except NoResultFound:
        oauth = OAuth(
            provider=provider_name,
            provider_user_id=provider_user_id,
            provider_user_login=provider_user_login,
            provider_data=json.dumps(profile['data']),
            token=token,
        )

    provider_label = profile['provider_label']

    if current_user.is_anonymous:
        if oauth.user:
            if not oauth.user.active:
                flash('Your account is disabled.', 'error')
                return redirect(url_for('user.login'))

            login_user(oauth.user)
            flash(f'Successfully signed in with {provider_label}.', 'success')
            return redirect(pop_safe_next_url())

        user = User(active=True)
        oauth.user = user
        db.session.add_all([user, oauth])
        db.session.commit()
        login_user(user)
        flash(f'Successfully signed in with {provider_label}.', 'success')
        return redirect(pop_safe_next_url())

    if oauth.user:
        if current_user != oauth.user:
            flash(
                f'The {provider_label} account ({provider_user_login}) has '
                'already been used to link to another account here.<br>'
                f'If you would like to access that account, sign out of this '
                f'account and log in using {provider_label}.',
                'error',
            )
            return redirect(url_for('main.user_profile_page'))
    else:
        oauth.user = current_user
        db.session.add(oauth)
        db.session.commit()
        flash(f'Successfully linked {provider_label} account.', 'success')
        return redirect(url_for('main.user_profile_page'))

    return False
