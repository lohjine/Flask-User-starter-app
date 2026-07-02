"""Steam OpenID sign-in support.

Steam sign-in uses OpenID 2.0 rather than OAuth. This module adapts the
verified Steam identity into the starter app's shared OAuth account-linking
model so Steam users can sign in and later link an email/password login.
"""

import re
from urllib.parse import urlencode

import requests
from flask import Blueprint, current_app, flash, redirect, request, url_for

from app.oauth.utils import handle_oauth_authorized


OPENID_ENDPOINT = 'https://steamcommunity.com/openid/login'
STEAM_ID_RE = re.compile(r'^https?://steamcommunity\.com/openid/id/(\d{17})/?$')

blueprint = Blueprint('steam', __name__)


@blueprint.route('/steam')
def login():
    """Redirect the user to Steam's OpenID provider."""
    return_to = url_for('steam.authorized', _external=True)
    realm = request.host_url.rstrip('/')
    params = {
        'openid.ns': 'http://specs.openid.net/auth/2.0',
        'openid.mode': 'checkid_setup',
        'openid.return_to': return_to,
        'openid.realm': realm,
        'openid.identity': 'http://specs.openid.net/auth/2.0/identifier_select',
        'openid.claimed_id': 'http://specs.openid.net/auth/2.0/identifier_select',
    }
    return redirect(f'{OPENID_ENDPOINT}?{urlencode(params)}')


@blueprint.route('/steam/authorized')
def authorized():
    """Verify Steam's OpenID assertion and sign in or link the local account."""
    if request.args.get('openid.mode') != 'id_res':
        flash('Failed to log in with Steam.', category='error')
        return redirect(url_for('user.login'))

    claimed_id = request.args.get('openid.claimed_id', '')
    match = STEAM_ID_RE.match(claimed_id)
    if not match:
        flash('Steam returned an invalid identity.', category='error')
        return redirect(url_for('user.login'))

    steam_id = match.group(1)
    if not _verify_openid_response(request.args):
        flash('Steam could not verify your sign-in.', category='error')
        return redirect(url_for('user.login'))

    profile = _load_profile(steam_id)
    return handle_oauth_authorized(
        'steam',
        {'steam_id': steam_id},
        {
            'id': steam_id,
            'login': profile.get('personaname') or steam_id,
            'provider_label': 'Steam',
            'data': profile,
        },
    )


def _verify_openid_response(args):
    verify_params = args.to_dict(flat=True)
    verify_params['openid.mode'] = 'check_authentication'
    try:
        response = requests.post(OPENID_ENDPOINT, data=verify_params, timeout=5)
        response.raise_for_status()
    except requests.RequestException:
        return False
    return 'is_valid:true' in response.text.splitlines()


def _load_profile(steam_id):
    profile = {'steamid': steam_id}
    api_key = current_app.config.get('STEAM_API_KEY')
    if not api_key:
        return profile

    try:
        response = requests.get(
            'https://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/',
            params={'key': api_key, 'steamids': steam_id},
            timeout=5,
        )
        response.raise_for_status()
    except requests.RequestException:
        return profile
    players = response.json().get('response', {}).get('players', [])
    if players:
        profile.update(players[0])
    return profile
