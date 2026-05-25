# Train Conductors

A small Django web app for managing players and selecting train conductors for Last War.

The app uses OpenID Connect (OIDC) login via `django-allauth`. Access is restricted by OIDC group membership.

## Features

- OIDC-based login
- Automatic Django user creation from OIDC accounts
- Group-based access control
- Admin/superuser mapping from OIDC groups
- Player database for conductor and VIP/Guardian Defender selection
- Docker-ready setup
- SQLite by default for simple deployments

## Tech Stack

- Python 3.13
- Django
- django-allauth
- uv
- SQLite
- Docker

## Local Development

Install dependencies:

```bash
uv sync
```

Run migrations:

```bash
uv run manage.py migrate
```

Start the development server:

```bash
uv run manage.py runserver
```

Open:

```text
http://127.0.0.1:8000/
```

## Docker

Build the image:

```bash
docker build -t train-conductors .
```

Run the container:

```bash
docker run --rm -it \
  -p 8000:8000 \
  --env-file .env \
  -v "$(pwd)/db.sqlite3:/app/db.sqlite3" \
  train-conductors
```

## Environment Variables

Create a `.env` file in the project root.

```env
DJANGO_SECRET_KEY=change-me
DJANGO_DEBUG=1

OIDC_PROVIDER_NAME=OIDC Login
OIDC_CLIENT_ID=your-client-id
OIDC_CLIENT_SECRET=your-client-secret
OIDC_SERVER_URL=https://your-oidc-provider.example.com/oidc
OIDC_TOKEN_AUTH_METHOD=client_secret_basic

OIDC_USER_GROUP=271u-management
OIDC_ADMIN_GROUP=271u-superuser
```

### Django

| Variable | Required | Description |
|---|---:|---|
| `DJANGO_SECRET_KEY` | Yes | Secret key used by Django. Use a strong random value outside development. |
| `DJANGO_DEBUG` | No | Set to `1` for local development. Use `0` in production. |

### OIDC

| Variable | Required | Description |
|---|---:|---|
| `OIDC_PROVIDER_NAME` | No | Display name for the OIDC provider. |
| `OIDC_CLIENT_ID` | Yes | Client ID from the OIDC provider. |
| `OIDC_CLIENT_SECRET` | Yes | Client secret from the OIDC provider. |
| `OIDC_SERVER_URL` | Yes | Base issuer/server URL of the OIDC provider. |
| `OIDC_TOKEN_AUTH_METHOD` | No | Token authentication method. Defaults to `client_secret_basic`. |

### OIDC Group Access

| Variable | Required | Description |
|---|---:|---|
| `OIDC_USER_GROUP` | Yes | Users in this OIDC group are allowed to log in. |
| `OIDC_ADMIN_GROUP` | Yes | Users in this OIDC group are granted Django staff and superuser rights. |

Current group mapping:

| OIDC group | Django effect |
|---|---|
| `271u-management` | Can log in |
| `271u-superuser` | Can log in, `is_staff=True`, `is_superuser=True` |
| Other users | Access denied |

The OIDC provider must include a `groups` claim in either the ID token or the UserInfo response.

Example claim:

```json
{
  "groups": [
    "271u-management",
    "271u-superuser"
  ]
}
```

## OIDC Redirect URI

Register this redirect URI in your OIDC provider:

```text
http://127.0.0.1:8000/accounts/oidc/oidc/login/callback/
```

For production, replace the host with your real domain.

## Admin

Django admin is available at:

```text
/admin/
```

Users in the configured admin OIDC group automatically receive Django staff and superuser rights on login.

## Notes

This project is currently designed as a small private/internal tool. Before exposing it publicly, review:

- `ALLOWED_HOSTS`
- HTTPS/TLS setup
- secure secret handling
- database persistence
- static file handling
- production WSGI/ASGI server setup
- OIDC provider claim configuration

## AI Disclaimer

Parts of this project were created with assistance from AI tooling. The generated code and documentation should be reviewed, tested, and maintained by a human before being used in production or for critical decisions.
