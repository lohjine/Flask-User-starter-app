# This file contains pytest 'fixtures'.
# If a test functions specifies the name of a fixture function as a parameter,
# the fixture function is called and its result is passed to the test function.
#
# Copyright 2014 SolidBuilds.com. All rights reserved
#
# Authors: Ling Thio <ling.thio@gmail.com>

import sys
from pathlib import Path

import pytest

workspace_root = Path(__file__).resolve().parents[2]
library_root = workspace_root / 'Flask-User'
sys.path.insert(0, str(library_root))

from app import create_app, db as the_db

# Initialize the Flask-App with test-specific settings
the_app = create_app(dict(
    TESTING=True,  # Propagate exceptions
    LOGIN_DISABLED=False,  # Enable @register_required
    MAIL_SUPPRESS_SEND=True,  # Disable Flask-Mail send
    SERVER_NAME='localhost',  # Enable url_for() without request context
    SQLALCHEMY_DATABASE_URI='sqlite:///:memory:',  # In-memory SQLite DB
    WTF_CSRF_ENABLED=False,  # Disable CSRF form validation
))

# Setup an application context (since the tests run outside of the webserver context)
the_app.app_context().push()

@pytest.fixture(scope='session')
def app():
    """ Makes the 'app' parameter available to test functions. """
    return the_app


@pytest.fixture(scope='session')
def db():
    """ Makes the 'db' parameter available to test functions. """
    from init_db import init_db

    init_db()
    return the_db


@pytest.fixture(scope='function')
def session(db):
    """Creates a new database session for a test."""
    from sqlalchemy.orm import scoped_session, sessionmaker

    connection = db.engine.connect()
    transaction = connection.begin()

    original_session = db.session
    session = scoped_session(sessionmaker(bind=connection))
    db.session = session

    try:
        yield session
    finally:
        session.remove()
        transaction.rollback()
        connection.close()
        db.session = original_session


@pytest.fixture(scope='session')
def client(app, db):
    return app.test_client()

