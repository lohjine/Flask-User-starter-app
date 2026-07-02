from flask import url_for

from app import db
from app.models.user_models import OAuth, User


LEGACY_BOOTSTRAP_FRAGMENTS = (
    b'has-error',
    b'help-block',
    b'btn-default',
    b'control-label',
)


def assert_modern_page(response):
    assert response.status_code == 200
    for fragment in LEGACY_BOOTSTRAP_FRAGMENTS:
        assert fragment not in response.data


def sign_out(client):
    client.get(url_for('user.logout'), follow_redirects=True)


def sign_in(client, email, password, next_url='/'):
    return client.post(
        url_for('user.login'),
        data={
            'email': email,
            'password': password,
            'next': next_url,
        },
        follow_redirects=True,
    )


def set_logged_in_user(client, user):
    with client.session_transaction() as session:
        session['_user_id'] = user.get_id()
        session['_fresh'] = True


def test_public_account_pages_render_with_bootstrap5_markup(app, client):
    sign_out(client)

    endpoints = (
        'user.login',
        'user.register',
        'user.forgot_password',
        'user.resend_email_confirmation',
    )

    for endpoint in endpoints:
        response = client.get(url_for(endpoint), follow_redirects=True)
        assert_modern_page(response)


def test_reset_and_confirm_email_pages_render(app, client):
    sign_out(client)
    user = User.query.filter_by(email='member@example.com').first()

    reset_token = app.user_manager.generate_reset_password_token(user)
    response = client.get(url_for('user.reset_password', token=reset_token), follow_redirects=True)
    assert_modern_page(response)

    confirm_token = app.user_manager.generate_confirm_email_token(user.id)
    response = client.get(url_for('user.confirm_email', token=confirm_token), follow_redirects=True)
    assert_modern_page(response)


def test_member_profile_and_change_password_pages_render(app, client):
    response = sign_in(client, 'member@example.com', 'Password1')
    assert_modern_page(response)

    for endpoint in ('main.member_page', 'main.user_profile_page', 'user.change_password'):
        response = client.get(url_for(endpoint), follow_redirects=True)
        assert_modern_page(response)


def test_admin_page_renders(app, client):
    response = sign_in(client, 'admin@example.com', 'Password1', url_for('main.admin_page'))
    assert_modern_page(response)

    response = client.get(url_for('main.admin_page'), follow_redirects=True)
    assert_modern_page(response)


def test_link_email_page_renders_for_oauth_user(app, client):
    user = User(active=True, password='')
    db.session.add(user)
    db.session.flush()

    oauth = OAuth(
        provider='google',
        provider_user_id='render-test-google-id',
        provider_user_login='render-test-google-user',
        token={},
        user=user,
    )
    db.session.add(oauth)
    db.session.commit()

    set_logged_in_user(client, user)

    response = client.get(url_for('user.linkemail'), follow_redirects=True)
    assert_modern_page(response)
