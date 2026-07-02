import flask

from app.oauth.utils import pop_safe_next_url


def test_oauth_next_url_is_sanitized(app):
    with app.test_request_context('/'):
        flask.session['next_url'] = 'https://evil.example/phish?x=1'

        assert pop_safe_next_url() == '/phish?x=1'
        assert 'next_url' not in flask.session


def test_oauth_next_url_defaults_to_home(app):
    with app.test_request_context('/'):
        assert pop_safe_next_url() == '/'
