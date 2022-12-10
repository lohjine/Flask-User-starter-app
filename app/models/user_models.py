# Copyright 2014 SolidBuilds.com. All rights reserved
#
# Authors: Ling Thio <ling.thio@gmail.com>

import flask
from flask_user import UserMixin
from flask_login import login_user
# from flask_user.forms import RegisterForm
from flask_wtf import FlaskForm
from flask_wtf.recaptcha import Recaptcha, RecaptchaField
from wtforms import StringField, SubmitField, validators, ValidationError

from app import db
from flask_user import UserManager
from flask_dance.consumer.storage.sqla import OAuthConsumerMixin
from sqlalchemy.orm.collections import attribute_mapped_collection

from flask import current_app, flash, redirect, render_template, request, url_for, abort
from flask_user import current_user, signals
from flask_user.forms import RegisterForm
from urllib.parse import quote, unquote    # Python 3

# Define the User data model. Make sure to add the flask_user.UserMixin !!
class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)

    # User authentication information (required for Flask-User)
    email = db.Column(db.Unicode(255), nullable=True, unique=True)
    email_confirmed_at = db.Column(db.DateTime())
    password = db.Column(db.String(255), nullable=False, server_default='')
    
    # reset_password_token = db.Column(db.String(100), nullable=False, server_default='')

    # User information
    active = db.Column('is_active', db.Boolean(), nullable=False, server_default='0')
    first_name = db.Column(db.Unicode(50), nullable=True) 
    last_name = db.Column(db.Unicode(50), nullable=True)

    # Relationships
    roles = db.relationship('Role', secondary='users_roles',
                            backref=db.backref('users', lazy='dynamic'))


class OAuth(OAuthConsumerMixin, db.Model):
    provider_user_id = db.Column(db.String(256), unique=True, nullable=False)
    provider_user_login = db.Column(db.String(255), nullable=False)
    provider_data = db.Column(db.String(), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey(User.id, ondelete='CASCADE'), nullable=False)
    user = db.relationship(User,
        # This `backref` thing sets up an `oauth` property on the User model,
        # which is a dictionary of OAuth models associated with that user,
        # where the dictionary key is the OAuth provider name.
        backref=db.backref(
            "oauth",
            collection_class=attribute_mapped_collection("provider"),
            cascade="all, delete-orphan",
        ),)

# Define the Role data model
class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(50), nullable=False, server_default=u'', unique=True)  # for @roles_accepted()
    label = db.Column(db.Unicode(255), server_default=u'')  # for display purposes


# Define the UserRoles association model
class UsersRoles(db.Model):
    __tablename__ = 'users_roles'
    id = db.Column(db.Integer(), primary_key=True)
    user_id = db.Column(db.Integer(), db.ForeignKey('users.id', ondelete='CASCADE'))
    role_id = db.Column(db.Integer(), db.ForeignKey('roles.id', ondelete='CASCADE'))


# # Define the User registration form
# # It augments the Flask-User RegisterForm with additional fields
# class MyRegisterForm(RegisterForm):
#     first_name = StringField('First name', validators=[
#         validators.DataRequired('First name is required')])
#     last_name = StringField('Last name', validators=[
#         validators.DataRequired('Last name is required')])




class UserManagerExtended(UserManager):
    
    def customize(self, app):
        # Configure customized forms
        
        self.USER_LINKEMAIL_TEMPLATE = 'flask_user/link_email.html'
        self.USER_AFTER_LINKEMAIL_ENDPOINT = 'main.user_profile_page'
        self.USER_LINKEMAIL_URL = '/user/link_email'
        self.LinkEmailFormClass = LinkEmailForm
        self.RegisterFormClass = RegisterFormExtended
        
        def linkemail_stub():
            if not self.USER_ENABLE_EMAIL: abort(404)
            return self.linkemail_view()
        
        app.add_url_rule(self.USER_LINKEMAIL_URL, 'user.linkemail', linkemail_stub,
                         methods=['GET', 'POST'])
        
    def linkemail_view(self):
        """ Display linkemail form to link email to User."""

        # if account already has confirmed email, redirect them
        if current_user.email_confirmed_at:
            return redirect(url_for('main.user_profile_page'))

        # Initialize form
        linkemail_form = self.LinkEmailFormClass(request.form)  # for register.html

        # Process valid POST
        if request.method == 'POST' and linkemail_form.validate():
            
            # Store password hash instead of password
            linkemail_form.password.data = self.hash_password(linkemail_form.password.data)
            
            # update email account to user
            linkemail_form.populate_obj(current_user)

            # Email confirmation depends on the USER_ENABLE_CONFIRM_EMAIL setting
            request_email_confirmation = self.USER_ENABLE_CONFIRM_EMAIL

            # Send 'registered' email and delete new User object if send fails
            if self.USER_SEND_REGISTERED_EMAIL:
                try:
                    # Send 'confirm email' or 'registered' email
                    self._send_link_email(current_user, current_user, request_email_confirmation)
                except Exception:
                    raise

            self.db_manager.commit()
            # Send user_link signal # Not yet implemented
#            signals.user_link.send(current_app._get_current_object(),
#                                         user=user)
            
            # password change invalidates token (see UserMixin.py), so just login user again
            login_user(current_user)

            return redirect(self._endpoint_url(self.USER_AFTER_LINKEMAIL_ENDPOINT))  # redirect to profile page

        # Render form
        self.prepare_domain_translations()
        return render_template(self.USER_LINKEMAIL_TEMPLATE,
                      form=linkemail_form,
                      linkemail_form=linkemail_form)

    def _send_link_email(self, user, user_email, request_email_confirmation):
#        um =  current_app.user_manager

        if self.USER_ENABLE_EMAIL and self.USER_SEND_REGISTERED_EMAIL:

            # Send 'registered' email, with or without a confirmation request
            self.email_manager.send_registered_email(user, user_email, request_email_confirmation)

            # Flash a system message
            if request_email_confirmation:
                email = user_email.email if user_email else user.email
                flash(_('A confirmation email has been sent to %(email)s with instructions to complete the creation of your email/password login.', email=email), 'success')
            else:
                flash(_('Email/password login successfully created.'), 'success')


    def unauthenticated_view(self):
        """ Prepare a Flash message and redirect to USER_UNAUTHENTICATED_ENDPOINT"""
        # Prepare Flash message
        url = request.url
        flash(_("You must be signed in to access '%(url)s'.", url=url), 'error')

        # Redirect to USER_UNAUTHENTICATED_ENDPOINT
        safe_next_url = self.make_safe_url(url)
        flask.session['next_url'] = safe_next_url # workaround for oauth login method
        return redirect(self._endpoint_url(self.USER_UNAUTHENTICATED_ENDPOINT)+'?next='+quote(safe_next_url))


    def _do_login_user(self, user, safe_next_url, remember_me=False):
        # User must have been authenticated
        if not user: return self.unauthenticated()

        # Check if user account has been disabled
        if not user.active:
            flash(_('Your account is disabled.'), 'error')
            return redirect(url_for('user.login'))

        # Check if user has a confirmed email address
        if self.USER_ENABLE_EMAIL \
                and self.USER_ENABLE_CONFIRM_EMAIL \
                and not current_app.user_manager.USER_ALLOW_LOGIN_WITHOUT_CONFIRMED_EMAIL \
                and not self.db_manager.user_has_confirmed_email(user):
            url = url_for('user.resend_email_confirmation')
            flash(_('Your email address has not yet been confirmed. Check your email Inbox and Spam folders for the confirmation email or <a href="%(url)s">Re-send confirmation email</a>.', url=url), 'error')
            return redirect(url_for('user.login'))

        # Use Flask-Login to sign in user
        # print('login_user: remember_me=', remember_me)
        login_user(user, remember=remember_me)

        # Send user_logged_in signal
        signals.user_logged_in.send(current_app._get_current_object(), user=user)

        # Flash a system message
        flash(_('You have signed in successfully.'), 'success')
        
        # clear next_url
        if 'next_url' in flask.session:
            flask.session.pop('next_url')

        # Redirect to 'next' URL
        return redirect(safe_next_url)


from wtforms import HiddenField, PasswordField
from flask_user.translation_utils import lazy_gettext as _    # map _() to lazy_gettext()
from flask_user.forms import unique_email_validator, password_validator

class LinkEmailForm(FlaskForm):
    """Link email form."""

    reg_next = HiddenField()

    email = StringField(_('Email'), validators=[
        validators.DataRequired(_('Email is required')),
        validators.Email(_('Invalid Email')),
        unique_email_validator])
    password = PasswordField(_('Password'), validators=[
        validators.DataRequired(_('Password is required')),
        password_validator])
    retype_password = PasswordField(_('Retype Password'), validators=[
        validators.EqualTo('password', message=_('Password and Retype Password did not match'))])

    submit = SubmitField(_('Link email'))

    def validate(self):
        if not super(LinkEmailForm, self).validate():
            return False
        # All is well
        return True


class RegisterFormExtended(RegisterForm):
    recaptcha = RecaptchaField(validators=[
        Recaptcha(message="Please fill in the captcha")])

# Define the User profile form
class UserProfileForm(FlaskForm):
    first_name = StringField('First name (optional)') #, validators=[validators.DataRequired('First name is required')])
    last_name = StringField('Last name (optional)') #, validators=[validators.DataRequired('Last name is required')])
    submit = SubmitField('Save')