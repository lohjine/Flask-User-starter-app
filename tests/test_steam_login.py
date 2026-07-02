from urllib.parse import parse_qs, urlparse

from flask import url_for

from app.models.user_models import OAuth


STEAM_ID = '76561198000000000'
CLAIMED_ID = f'https://steamcommunity.com/openid/id/{STEAM_ID}'


class ResponseStub:
    def __init__(self, text='', payload=None):
        self.text = text
        self.payload = payload or {}

    def raise_for_status(self):
        return None

    def json(self):
        return self.payload


def steam_authorized_query():
    return {
        'openid.ns': 'http://specs.openid.net/auth/2.0',
        'openid.mode': 'id_res',
        'openid.op_endpoint': 'https://steamcommunity.com/openid/login',
        'openid.claimed_id': CLAIMED_ID,
        'openid.identity': CLAIMED_ID,
        'openid.return_to': 'http://localhost/login/steam/authorized',
        'openid.response_nonce': 'nonce',
        'openid.assoc_handle': 'handle',
        'openid.signed': 'signed',
        'openid.sig': 'signature',
    }


def test_steam_login_redirects_to_openid_provider(app, client):
    response = client.get(url_for('steam.login'))

    assert response.status_code == 302
    location = urlparse(response.location)
    params = parse_qs(location.query)

    assert location.scheme == 'https'
    assert location.netloc == 'steamcommunity.com'
    assert location.path == '/openid/login'
    assert params['openid.mode'] == ['checkid_setup']
    assert params['openid.return_to'] == ['http://localhost/login/steam/authorized']
    assert params['openid.identity'] == [
        'http://specs.openid.net/auth/2.0/identifier_select'
    ]


def test_steam_authorized_creates_local_user(app, client, session, monkeypatch):
    def post_stub(url, data, timeout):
        assert url == 'https://steamcommunity.com/openid/login'
        assert data['openid.mode'] == 'check_authentication'
        assert timeout == 5
        return ResponseStub('ns:http://specs.openid.net/auth/2.0\nis_valid:true\n')

    def get_stub(url, params, timeout):
        assert params['steamids'] == STEAM_ID
        assert timeout == 5
        return ResponseStub(
            payload={
                'response': {
                    'players': [
                        {
                            'steamid': STEAM_ID,
                            'personaname': 'Steam Display Name',
                        }
                    ]
                }
            }
        )

    monkeypatch.setitem(app.config, 'STEAM_API_KEY', 'test-steam-key')
    monkeypatch.setattr('app.oauth.steam.requests.post', post_stub)
    monkeypatch.setattr('app.oauth.steam.requests.get', get_stub)

    response = client.get(
        url_for('steam.authorized'),
        query_string=steam_authorized_query(),
    )

    oauth = OAuth.query.filter_by(provider='steam', provider_user_id=STEAM_ID).one()

    assert response.status_code == 302
    assert response.location == '/'
    assert oauth.user.active is True
    assert oauth.user.email is None
    assert oauth.provider_user_login == 'Steam Display Name'


def test_steam_authorized_rejects_unverified_identity(app, client, session, monkeypatch):
    def post_stub(url, data, timeout):
        return ResponseStub('ns:http://specs.openid.net/auth/2.0\nis_valid:false\n')

    monkeypatch.setattr('app.oauth.steam.requests.post', post_stub)

    response = client.get(
        url_for('steam.authorized'),
        query_string=steam_authorized_query(),
    )

    assert response.status_code == 302
    assert response.location == '/user/sign-in'
    assert OAuth.query.filter_by(provider='steam', provider_user_id=STEAM_ID).first() is None
