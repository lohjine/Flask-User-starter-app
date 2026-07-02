## Changes in fork

* Upgraded package versions, e.g. Flask -> 3.*
* Upgraded Bootstrap to v5
* Added OAuth/OpenID support (Google, Facebook, Steam)
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

This checkout is expected to live beside the sibling `Flask-User/` library
source:

    parent/
      Flask-User/
      Flask-User-starter-app/

    # Clone the code repository
    git clone https://github.com/lohjine/Flask-User-starter-app.git
	cd Flask-User-starter-app

    # Create virtual environment
    python -m venv .venv
    .venv\Scripts\Activate.ps1

    # Install required Python packages
    python -m pip install -r requirements.txt

The requirements install the sibling `../Flask-User` library in editable mode.
This keeps the starter app and local Flask-User source synchronized during
development.


## Configuring local settings

Copy the `local_settings_example.py` file to `local_settings.py`.

    cp app/local_settings_example.py app/local_settings.py

Edit the `local_settings.py` file for your database, mail server, OAuth/OpenID
providers, Recaptcha keys, and production safety settings.

Set `SECRET_KEY` to a unique production secret with at least 32 bytes of text.
For example:

    python -c "import secrets; print(secrets.token_urlsafe(48))"

For production, also configure persistent rate-limit storage with
`RATELIMIT_STORAGE_URI`, set `OAUTHLIB_INSECURE_TRANSPORT = '0'`, and use SMTP
credentials intended for application mail instead of a personal password.


## Initializing the Database

    # Create DB tables and populate the roles and users tables
    python init_db.py

    # Optional: create migration infrastructure for an app you are developing
    flask db init


## Migrating Database

	# Do a backup, e.g.
	sqlite3 app.db .backup backup_app.db
	
	# Creating a migration
	flask db migrate -m "changes"
	
	# Check migrations/versions/*.py for correct migration generation, then
	flask db upgrade


## Running the app

    # Start the Flask development web server
    flask --app flask_app.py run -h 0.0.0.0 -p 5000

Point your web browser to http://localhost:5000/

You can make use of the following users:
- email `member@example.com` with password `Password1`.
- email `admin@example.com` with password `Password1`.


## Running the automated tests

    python -m pytest tests -q


## OAuth and Steam support

This starter app supports Google and Facebook OAuth through Flask-Dance when
the matching client ID and client secret are configured in `app/local_settings.py`.
It also supports Steam sign-in through Steam OpenID. Steam login does not
require OAuth client credentials; set `STEAM_OPENID_ENABLED = False` to disable
it. `STEAM_API_KEY` is optional and is only used to fetch a Steam display name
for the linked account.

OAuth/OpenID-created users may start without an email address or password; they
can add email/password login later from the profile page.

GitHub OAuth is intentionally unsupported in this starter app. The placeholder
module remains unavailable until it is redesigned against the current `User`
and `OAuth` models.


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
