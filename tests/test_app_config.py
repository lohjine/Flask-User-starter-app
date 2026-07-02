from pathlib import Path

import flask_user


def test_starter_app_uses_sibling_flask_user(app):
    workspace_root = Path(__file__).resolve().parents[2]
    library_root = workspace_root / 'Flask-User'

    assert library_root.resolve() in Path(flask_user.__file__).resolve().parents


def test_registration_config_uses_flask_user_setting(app):
    assert app.config['USER_ENABLE_REGISTER'] is True
    assert app.config['USER_ENABLE_REGISTRATION'] == app.config['USER_ENABLE_REGISTER']
