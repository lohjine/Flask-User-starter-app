"""OAuth providers enabled by this starter app.

GitHub is intentionally not exported. See app.oauth.github for the unsupported
placeholder and rationale.
"""

from .google import blueprint as google_blueprint
from .facebook import blueprint as facebook_blueprint
from .utils import SUPPORTED_PROVIDERS
