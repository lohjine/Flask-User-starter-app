"""GitHub OAuth is not supported by this starter app.

Google and Facebook are the active OAuth providers. The previous GitHub
implementation referenced model fields and imports that do not exist in this
app, so it is kept unavailable until it can be redesigned deliberately.
"""

SUPPORTED = False


def create_blueprint(*args, **kwargs):
    raise RuntimeError(
        'GitHub OAuth is not supported by this starter app. '
        'Use Google or Facebook, or implement GitHub against the current User '
        'and OAuth models first.'
    )
