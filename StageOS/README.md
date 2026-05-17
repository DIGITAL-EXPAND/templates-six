# StageOS

## Backend Settings

The default `stageos.settings` module is safe for local backend development and test data only.

Environment controls:

- `STAGEOS_ENV`: `local`, `test`, `staging`, or `production`.
- `SECRET_KEY`: required for staging and production.
- `DEBUG`: explicit boolean override.
- `ALLOWED_HOSTS`: comma-separated host list.
- `DB_ENGINE`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`: database connection settings.
- `JWT_ACCESS_TOKEN_MINUTES`, `JWT_REFRESH_TOKEN_DAYS`: token lifetime controls.
- `STAGEOS_MAX_UPLOAD_BYTES`, `STAGEOS_ALLOWED_UPLOAD_MIME_TYPES`: upload policy controls used by backend validation.
- `CSRF_TRUSTED_ORIGINS`, `STAGEOS_FRONTEND_ORIGINS`: placeholders for the future separate frontend origin strategy.

Settings entry points are available as `stageos.settings_local`, `stageos.settings_test`, `stageos.settings_staging`, and `stageos.settings_production`. Production and staging settings enable secure cookies, SSL redirect, and HSTS defaults.
