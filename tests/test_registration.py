"""Registration must work without reCAPTCHA keys and show its errors."""

import pytest

from app.models.user_models import User


@pytest.fixture()
def production_like(app):
    """No reCAPTCHA keys, and testing mode off (Flask-WTF skips reCAPTCHA when testing)."""
    saved = {key: app.config.get(key) for key in ('RECAPTCHA_PUBLIC_KEY', 'RECAPTCHA_PRIVATE_KEY')}
    app.config.update(RECAPTCHA_PUBLIC_KEY='', RECAPTCHA_PRIVATE_KEY='', TESTING=False)
    app.testing = False
    try:
        yield app
    finally:
        app.config.update(saved, TESTING=True)
        app.testing = True


def test_registration_without_recaptcha_keys(production_like, client, session):
    response = client.post('/user/register', data={
        'email': 'no-captcha@example.com',
        'password': 'Password1',
        'retype_password': 'Password1',
    })
    assert response.status_code == 302
    assert User.query.filter_by(email='no-captcha@example.com').first() is not None


def test_registration_errors_are_listed(client, session):
    response = client.post('/user/register', data={
        'email': 'not-an-email',
        'password': 'Password1',
        'retype_password': 'different',
    })
    assert response.status_code == 200
    assert b'alert-danger' in response.data
