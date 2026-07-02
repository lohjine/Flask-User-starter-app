from flask import get_flashed_messages
from flask_login import login_user, logout_user

from app import db
from app.models.user_models import OAuth, User
from app.oauth.utils import handle_oauth_authorized


def _profile(provider_label='Facebook', user_id='provider-user-id', login='Provider User'):
    return {
        'id': user_id,
        'login': login,
        'provider_label': provider_label,
        'data': {'id': user_id, 'name': login},
    }


def test_oauth_authorized_creates_local_user_for_anonymous_login(app, session):
    with app.test_request_context('/login/facebook/authorized'):
        logout_user()

        response = handle_oauth_authorized(
            'facebook',
            {'access_token': 'token'},
            _profile(user_id='new-facebook-id'),
        )

        oauth = OAuth.query.filter_by(
            provider='facebook',
            provider_user_id='new-facebook-id',
        ).one()

        assert response.status_code == 302
        assert response.location == '/'
        assert oauth.user.active is True
        assert oauth.user.email is None
        assert oauth.provider_user_login == 'Provider User'


def test_oauth_authorized_logs_in_linked_user(app, session):
    user = User(active=True)
    oauth = OAuth(
        provider='google',
        provider_user_id='linked-google-id',
        provider_user_login='linked@example.com',
        token={'access_token': 'token'},
        user=user,
    )
    db.session.add_all([user, oauth])
    db.session.commit()

    with app.test_request_context('/login/google/authorized'):
        logout_user()

        response = handle_oauth_authorized(
            'google',
            {'access_token': 'token'},
            _profile('Google', 'linked-google-id', 'linked@example.com'),
        )

        assert response.status_code == 302
        assert response.location == '/'


def test_oauth_authorized_rejects_disabled_linked_user(app, session):
    user = User(active=False)
    oauth = OAuth(
        provider='google',
        provider_user_id='disabled-google-id',
        provider_user_login='disabled@example.com',
        token={'access_token': 'token'},
        user=user,
    )
    db.session.add_all([user, oauth])
    db.session.commit()

    with app.test_request_context('/login/google/authorized'):
        logout_user()

        response = handle_oauth_authorized(
            'google',
            {'access_token': 'token'},
            _profile('Google', 'disabled-google-id', 'disabled@example.com'),
        )

        assert response.status_code == 302
        assert response.location == '/user/sign-in'
        assert ('error', 'Your account is disabled.') in get_flashed_messages(
            with_categories=True
        )


def test_oauth_collision_message_uses_login_without_email(app, session):
    linked_user = User(active=True)
    current = User(active=True)
    oauth = OAuth(
        provider='facebook',
        provider_user_id='collision-facebook-id',
        provider_user_login='Facebook Display Name',
        token={'access_token': 'token'},
        user=linked_user,
    )
    db.session.add_all([linked_user, current, oauth])
    db.session.commit()

    with app.test_request_context('/login/facebook/authorized'):
        login_user(current)

        response = handle_oauth_authorized(
            'facebook',
            {'access_token': 'token'},
            _profile(
                'Facebook',
                'collision-facebook-id',
                'Facebook Display Name',
            ),
        )

        messages = get_flashed_messages(with_categories=True)

        assert response.status_code == 302
        assert response.location == '/main/profile'
        assert messages[0][0] == 'error'
        assert 'Facebook Display Name' in messages[0][1]
