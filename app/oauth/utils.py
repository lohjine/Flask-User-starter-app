import flask


def pop_safe_next_url(default='/'):
    next_url = flask.session.pop('next_url', default)
    return flask.current_app.user_manager.make_safe_url(next_url)
