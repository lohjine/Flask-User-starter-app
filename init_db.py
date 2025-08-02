
import datetime

from flask import current_app
import core  # Import core to apply monkey patch
from app import create_app
from app import db
from app.models.user_models import User, Role

def init_db():
    """ Initialize the database."""
    db.drop_all()
    db.create_all()
    create_users()


def create_users():
    """ Create users """

    # Create all tables
    db.create_all()

    # Adding roles
    admin_role = find_or_create_role('admin', u'Admin')

    # Add users
    user = find_or_create_user(u'Admin', u'Example', u'admin@example.com', 'Password1', admin_role)
    user = find_or_create_user(u'Member', u'Example', u'member@example.com', 'Password1')

    # Save to DB
    db.session.commit()


def find_or_create_role(name, label):
    """ Find existing role or create new role """
    role = Role.query.filter(Role.name == name).first()
    if not role:
        role = Role(name=name, label=label)
        db.session.add(role)
    return role


def find_or_create_user(first_name, last_name, email, password, role=None):
    """ Find existing user or create new user """
    user = User.query.filter(User.email == email).first()
    if not user:
        user = User(email=email,
                    first_name=first_name,
                    last_name=last_name,
                    password=current_app.user_manager.password_manager.hash_password(password),
                    active=True,
                    email_confirmed_at=datetime.datetime.utcnow())
        if role:
            user.roles.append(role)
        db.session.add(user)
    return user

if __name__ == '__main__':
    
    app = create_app()
    
    with app.app_context():
        init_db()
        print('db init complete')



