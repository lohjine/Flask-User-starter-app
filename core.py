
# Monkey patch bcrypt compatibility
try:
    import bcrypt
    if not hasattr(bcrypt, '__about__'):
        bcrypt.__about__ = type('__about__', (), {'__version__': bcrypt.__version__})
except ImportError:
    pass

from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
#
limiter = Limiter(key_func=get_remote_address)

                      # storage_uri="redis://localhost:6379", # rmb to include redis in requirements.txt
                      # key_prefix='buyfriendmoe',
                      # strategy="fixed-window")