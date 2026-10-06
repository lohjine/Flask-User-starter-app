# Changelog

## Unreleased

- Fixed registration silently failing when no reCAPTCHA keys are configured: the hidden
  captcha field was still required, so the form re-rendered without any visible error. The
  field is now dropped without keys, and all form errors are listed above the form.
- Added Steam OpenID sign-in and account linking alongside Google and Facebook OAuth.
- Updated the starter app for the modern Flask 3 / Flask-SQLAlchemy 3 dependency path.
- Switched development installs to the sibling `../Flask-User` source in editable mode.
- Refreshed starter-app account templates for Bootstrap 5 and added page-render coverage.
- Documented stronger production secret-key, OAuth, rate-limit, and optional-integration expectations.
