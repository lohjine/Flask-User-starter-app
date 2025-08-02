## Changes in fork

* Upgraded package versions, e.g. Flask -> 3.*
* Upgraded bootstrap to v5
* Added OAuth support (google, facebook)
* Added Flask Limiter support (see core.py)
* Added error log to logs/ directory
* Changed First name/Last name to be optional, since default register form does not have either field
* Added recaptcha v2 support

# Flask-User starter app v1.0

This code base serves as starting point for writing your next Flask application.

This branch is for Flask-User v1.0.

## Code characteristics

* Well organized directories with lots of comments
    * app
        * commands
        * models
        * static
        * templates
        * views
    * tests
* Includes database migration framework (`alembic`)
* Sends error emails to admins for unhandled exceptions

## Setting up a development environment

We assume that you have `git` and `virtualenv` installed.

    # Clone the code repository
    git clone https://github.com/lohjine/Flask-User-starter-app.git
	cd Flask-User-starter-app

    # Create virtual environment
    python3 -m virtualenv venv
	source venv/bin/activate

    # Install required Python packages
    pip install -r requirements.txt


# Configuring SMTP

Copy the `local_settings_example.py` file to `local_settings.py`.

    cp app/local_settings_example.py app/local_settings.py

Edit the `local_settings.py` file.

Specifically set all the MAIL_... settings to match your SMTP settings

Note that Google's SMTP server requires the configuration of "less secure apps".
See https://support.google.com/accounts/answer/6010255?hl=en

Note that Yahoo's SMTP server requires the configuration of "Allow apps that use less secure sign in".
See https://help.yahoo.com/kb/SLN27791.html


## Initializing the Database

    # Create DB tables and populate the roles and users tables
    python init_db.py # Creates all tables from scratch
	flask db init # Creates migration infrastructure


## Migrating Database

	# Do a backup, e.g.
	sqlite3 app.db .backup backup_app.db
	
	# Creating a migration
	flask db migrate -m "changes"
	
	# Check migrations/versions/*.py for correct migration generation, then
	flask db upgrade


## Running the app

    # Start the Flask development web server
    flask run -h 0.0.0.0 -p 5000

Point your web browser to http://localhost:5000/

You can make use of the following users:
- email `user@example.com` with password `Password1`.
- email `admin@example.com` with password `Password1`.


## Running the automated tests

    # Start the Flask development web server
    py.test tests/


## Trouble shooting

If you make changes in the Models and run into DB schema issues, delete the sqlite DB file `app.sqlite`.


## See also

* [FlaskDash](https://github.com/twintechlabs/flaskdash) is a starter app for Flask
  with [Flask-User](https://readthedocs.org/projects/flask-user/)
  and [CoreUI](https://coreui.io/) (A Bootstrap Admin Template).

## Acknowledgements

With thanks to the following Flask extensions:

* [Alembic](http://alembic.zzzcomputing.com/)
* [Flask](http://flask.pocoo.org/)
* [Flask-Login](https://flask-login.readthedocs.io/)
* [Flask-Migrate](https://flask-migrate.readthedocs.io/)
* [Flask-Script](https://flask-script.readthedocs.io/)
* [Flask-User](http://flask-user.readthedocs.io/en/v0.6/)

<!-- Please consider leaving this line. Thank you -->
[Flask-User-starter-app](https://github.com/lingthio/Flask-User-starter-app) was used as a starting point for this code repository.


## Authors

- Ling Thio -- ling.thio AT gmail DOT com