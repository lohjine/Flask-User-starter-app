""" This module defines Flask-User decorators
such as @login_required, @roles_accepted and @roles_required and @confirmed_email_required.
"""

# Author: Ling Thio <ling.thio@gmail.com>
# Copyright (c) 2013 Ling Thio

from functools import wraps
from flask import current_app, g
from flask_login import current_user

def _is_logged_in_with_confirmed_email_or_oauth(user_manager):
    """| Returns True if user is logged in and has a confirmed email address.
    | Returns False otherwise.
    """
    # User must be logged in
    if user_manager.call_or_get(current_user.is_authenticated):
        # Is unconfirmed email allowed for this view by @allow_unconfirmed_email?
        unconfirmed_email_allowed = \
            getattr(g, '_flask_user_allow_unconfirmed_email', False)
        
        # unconfirmed_email_allowed must be True or
        # User must have at least one confirmed email address, or one of the oauth
        google_oauth = False
        facebook_oauth = False
        if 'google' in current_user.oauth:
            google_oauth = True

        if 'facebook' in current_user.oauth:
            facebook_oauth = True
        
        if unconfirmed_email_allowed or user_manager.db_manager.user_has_confirmed_email(current_user) or google_oauth or facebook_oauth:
            return True

    return False


def login_required(view_function):
    """ This decorator ensures that the current user is logged in, with support for oauth

    Example::

        @route('/member_page')
        @login_required
        def member_page():  # User must be logged in
            ...

    If USER_ENABLE_EMAIL is True and USER_ENABLE_CONFIRM_EMAIL is True,
    this view decorator also ensures that the user has a confirmed email address.

    | Calls unauthorized_view() when the user is not logged in
        or when the user has not confirmed their email address.
    | Calls the decorated view otherwise.
    """
    @wraps(view_function)    # Tells debuggers that is is a function wrapper
    def decorator(*args, **kwargs):
        user_manager = current_app.user_manager
        
        # User must be logged in with a confirmed email address
        allowed = _is_logged_in_with_confirmed_email_or_oauth(user_manager)
        if not allowed:
            # Redirect to unauthenticated page
            return user_manager.unauthenticated_view()

        # It's OK to call the view
        return view_function(*args, **kwargs)

    return decorator
