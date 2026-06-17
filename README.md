# alliance-management

Alliance Management is a Django-based management tool for Last War alliances. It helps alliance leadership keep a structured player roster, track current and former members, document player-specific notes, review audit logs, and manage alliance workflows such as train conductor rotation.

The project is designed as a practical internal alliance operations tool, but the setup is intentionally understandable and open-source friendly: Django, OIDC login, SQLite or PostgreSQL, a small TypeScript frontend build, Docker support, and repeatable development commands through Task.

## What the project does

- Shows an alliance dashboard with member counts, total and average strength, rank distribution, recent joins, recent leaves, rotation status, top players, and latest player-sync information.
- Stores players with in-game name, Last War ID, alliance rank, strength, member status, join/leave timestamps, conductor eligibility, VIP/Guardian Defender eligibility, and reliability score.
- Tracks past usernames when a player changes their in-game name during a sync.
- Provides member and non-member overviews.
- Provides case-insensitive player search and player detail pages.
- Supports comments on players, including soft deletion by staff users.
- Manages a train conductor rotation for eligible R4/R5 players.
- Allows rotation entries to be added, reordered, and removed.
- Writes audit logs for player changes and rotation changes.
- Synchronizes player data from the LastWar Tools alliance members API.
- Stores each player sync run with status, counts, timestamps, and error messages.
- Uses OpenID Connect login through django-allauth.
- Restricts access by OIDC group membership.
- Maps configured OIDC admin groups to Django staff and superuser permissions.
- Provides a health endpoint for container health checks.

## Tech stack

- Python 3.13
- Django 6
- django-allauth with OpenID Connect
- Pydantic for parsing LastWar Tools API responses
- SQLite for simple local deployments
- PostgreSQL for production-style deployments
- psycopg for PostgreSQL support
- WhiteNoise for static files
- Gunicorn for the container runtime
- Sentry SDK / GlitchTip-compatible error reporting support
- TypeScript for frontend scripts
- uv for Python dependency management
- pnpm for JavaScript dependency management in the Taskfile
- Task for repeatable development commands
- Docker and Docker Compose for deployment

## Repository layout

| Path | Purpose |
|---|---|
| `config/settings.py` | Main Django settings, authentication, static files, logging, Sentry, OIDC, and branding configuration. |
| `config/database.py` | SQLite/PostgreSQL database configuration builder. |
| `config/urls.py` | URL routes and Django admin branding. |
| `core/models/` | Database models and Pydantic API models. |
| `core/services/game_client.py` | LastWar Tools API client. |
| `core/services/player_sync.py` | Player sync logic that creates, updates, joins, leaves, and records sync runs. |
| `core/management/commands/sync_players.py` | Django management command for manual or scheduled player syncs. |
| `core/views/` | Page and JSON API views. |
| `templates/` | Django templates. |
| `typescript/` | TypeScript source files. |
| `core/static/core/js/` | Compiled JavaScript output. |
| `docker/entrypoint.sh` | Container entrypoint; optionally runs migrations before starting the app. |
| `docker/player_sync.sh` | Looping player sync worker script. |
| `examples/docker-compose-rootless.yml` | Example Docker Compose deployment with app, sync worker, PostgreSQL, and Traefik labels. |
| `taskfile.yaml` | Development automation commands. |
| `Dockerfile` | Multi-stage production image build. |

## Requirements for development

Install these tools locally:

- Python 3.13
- uv
- Node.js
- pnpm
- Task

Optional but useful:

- Docker or Podman
- Docker Compose
- PostgreSQL, if you want to develop against PostgreSQL instead of SQLite
- An OIDC provider for real login testing
- A LastWar Tools API key and alliance ID for player synchronization

The app can start with SQLite, but normal UI access expects OIDC to be configured because the project is set up for social/OIDC login instead of a local username/password signup flow.

## Quick start for local development

Create a local environment file:

```env
APP_NAME=Alliance Management
DJANGO_SECRET_KEY=replace-this-with-a-development-secret
DJANGO_DEBUG=1
DJANGO_ALLOWED_HOSTS=127.0.0.1,localhost
DJANGO_CSRF_TRUSTED_ORIGINS=http://127.0.0.1:8000,http://localhost:8000

DATABASE_ENGINE=sqlite
SQLITE_PATH=data/db.sqlite3

OIDC_PROVIDER_NAME=OIDC Login
OIDC_CLIENT_ID=your-client-id
OIDC_CLIENT_SECRET=your-client-secret
OIDC_SERVER_URL=https://your-oidc-provider.example.com
OIDC_TOKEN_AUTH_METHOD=client_secret_basic
OIDC_USER_GROUP=server-management
OIDC_ADMIN_GROUP=server-superuser

LASTWAR_TOOLS_BASEURL=https://api.lastwar.tools
LASTWAR_TOOLS_APIKEY=your-api-key
LASTWAR_TOOLS_ALLIANCEID=your-alliance-id
```

Install dependencies, compile TypeScript, create/apply migrations, and run checks:

```bash
task setup
```

Run the development server:

```bash
DJANGO_DEBUG=1 uv run python manage.py runserver
```

Open the app at:

```text
http://127.0.0.1:8000/
```

Run a quick Django configuration check:

```bash
task check
```

Compile TypeScript after frontend changes:

```bash
task javascript:compile
```

## Taskfile commands

The Taskfile loads `.env` automatically and provides the recommended project workflows.

| Task | What it does |
|---|---|
| `task install` | Installs Python and JavaScript dependencies. |
| `task python:install-dependencies` | Runs `uv sync`. |
| `task javascript:install-dependencies` | Runs `pnpm i --frozen-lockfile`. |
| `task setup` | Installs dependencies, compiles TypeScript, creates migrations, applies migrations, and runs Django checks. |
| `task check` | Runs `uv run python manage.py check`. |
| `task run` | Runs the app in production-like local mode: installs dependencies, builds TypeScript, collects static files, and starts Django runserver with `DJANGO_DEBUG=0`. |
| `task javascript:compile` | Runs the TypeScript compiler. |
| `task django:create-migrations` | Runs `python manage.py makemigrations` through uv. |
| `task django:run-migrations` | Runs `python manage.py migrate` through uv. |
| `task manage:sync_players` | Runs the LastWar Tools player synchronization command. |
| `task clean` | Removes Python bytecode, `.venv/`, and `node_modules/`. |
| `task pack` | Creates `../project.tar` with the project files used for sharing/export. |

For day-to-day development, `task setup` and `task check` are the most useful commands. For local debug serving, prefer running `DJANGO_DEBUG=1 uv run python manage.py runserver` directly, because `task run` intentionally overrides `DJANGO_DEBUG` to `0`.

## Environment variables

Boolean values are parsed as true when set to `1`, `true`, `yes`, or `on`. Any other value is treated as false. List/set variables are comma-separated.

### Application and Django settings

| Variable | Default | Required | Description |
|---|---:|---:|---|
| `APP_NAME` | `Alliance Management` | No | Display name used for page branding and Django admin titles. |
| `DJANGO_SECRET_KEY` | `dev-only-secret-key` | Yes in production | Django secret key. Use a long random secret outside local development. |
| `DJANGO_DEBUG` | `False` | No | Enables Django debug mode when true. Keep false in production. |
| `RUNNING_IN_CONTAINER` | `False` | No | Changes log formatting for container output. The Dockerfile sets this to true. |
| `DJANGO_ALLOWED_HOSTS` | `127.0.0.1,localhost` | Yes in production | Comma-separated Django allowed hosts. |
| `DJANGO_CSRF_TRUSTED_ORIGINS` | empty | Yes behind HTTPS/proxies | Comma-separated trusted origins including scheme, for example `https://alliance.example.com`. |
| `SENTRY_DSN` | empty | No | Enables Sentry/GlitchTip reporting when set. |
| `SENTRY_LOGGING` | `False` | No | Enables Sentry log capture through `sentry_sdk.init(enable_logs=...)` when Sentry is configured. |

### Database settings

| Variable | Default | Required | Description |
|---|---:|---:|---|
| `DATABASE_ENGINE` | `sqlite` | No | Database backend. Supported values are `sqlite`, `postgres`, and `postgresql`. |
| `SQLITE_PATH` | `data/db.sqlite3` under the project root | No, SQLite only | SQLite database file path. In Docker, mount `/app/data` if you use the default. |
| `POSTGRES_DB` | none | Yes, PostgreSQL only | PostgreSQL database name. |
| `POSTGRES_USER` | none | Yes, PostgreSQL only | PostgreSQL user. |
| `POSTGRES_PASSWORD` | none | Yes, PostgreSQL only | PostgreSQL password. |
| `POSTGRES_HOST` | `db` | No, PostgreSQL only | PostgreSQL host. The example Compose file uses a service named `db`. |
| `POSTGRES_PORT` | `5432` | No, PostgreSQL only | PostgreSQL port. |
| `POSTGRES_CONN_MAX_AGE` | `60` | No, PostgreSQL only | Django persistent database connection lifetime in seconds. |

### OIDC authentication settings

| Variable | Default | Required | Description |
|---|---:|---:|---|
| `OIDC_PROVIDER_NAME` | `OIDC Login` | No | Display name shown for the OpenID Connect provider. |
| `OIDC_CLIENT_ID` | empty | Yes | Client ID from your OIDC provider. |
| `OIDC_CLIENT_SECRET` | empty | Yes | Client secret from your OIDC provider. |
| `OIDC_SERVER_URL` | empty | Yes | OIDC issuer/server URL used by django-allauth. |
| `OIDC_TOKEN_AUTH_METHOD` | `client_secret_basic` | No | Token endpoint authentication method. Keep the default unless your provider requires another method. |
| `OIDC_USER_GROUP` | `server-management` | Yes for real access control | Comma-separated group names allowed to log in. |
| `OIDC_ADMIN_GROUP` | `server-superuser` | Yes for admin mapping | Comma-separated group names that receive Django `is_staff=True` and `is_superuser=True` on login. |

Important: the OIDC groups claim name is currently hard-coded in `config/settings.py` as `groups` via `OIDC_GROUPS_CLAIM = "groups"`. It is not currently read from an environment variable. The adapter can also read nested claim names if the setting is changed in code, for example `realm_access.roles`.

The OIDC provider ID is hard-coded as `oidc`, so the callback URL contains two `oidc` path segments.

Local callback URL:

```text
http://127.0.0.1:8000/accounts/oidc/oidc/login/callback/
```

Production callback URL:

```text
https://alliance.example.com/accounts/oidc/oidc/login/callback/
```

Group behavior:

| OIDC membership | Result |
|---|---|
| Member of any `OIDC_USER_GROUP` | User can log in. |
| Member of any `OIDC_ADMIN_GROUP` | User can log in and becomes Django staff/superuser. |
| Member of neither | Access is denied with HTTP 403. |

### LastWar Tools API settings

| Variable | Default | Required | Description |
|---|---:|---:|---|
| `LASTWAR_TOOLS_BASEURL` | `https://api.lastwar.tools` | No | Base URL for the LastWar Tools API. Trailing slashes are removed automatically. |
| `LASTWAR_TOOLS_APIKEY` | empty | Yes for sync | API key sent as the `X-API-Key` header. |
| `LASTWAR_TOOLS_ALLIANCEID` | empty | Yes for sync | Alliance ID used in the `/alliance/{alliance_id}/members` API request. |

The sync client requests alliance members sorted by power in descending order and validates the response with Pydantic before updating the database.

### Container and sync worker settings

| Variable | Default | Required | Description |
|---|---:|---:|---|
| `RUN_MIGRATIONS` | `1` | No | Used by `docker/entrypoint.sh`. When `1`, the container runs `python manage.py migrate --noinput` before starting the command. Set to `0` for worker containers that should not run migrations. |
| `PLAYER_SYNC_INTERVAL_SECONDS` | `10800` | No | Used by `docker/player_sync.sh`. Time between sync runs. Default is 3 hours. |
| `PLAYER_SYNC_INITIAL_DELAY_SECONDS` | `120` | No | Used by `docker/player_sync.sh`. Delay before the first sync run, useful while the web app and database become healthy. |

## Player synchronization

Run a manual player sync:

```bash
uv run python manage.py sync_players
```

Run a dry run:

```bash
uv run python manage.py sync_players --dry-run
```

Or use the Taskfile alias:

```bash
task manage:sync_players
```

During a sync, the app:

1. Fetches alliance members from LastWar Tools.
2. Creates missing players.
3. Updates existing player name, rank, strength, and join timestamp.
4. Stores the previous name as a past username when a player is renamed.
5. Marks returned players as current alliance members.
6. Marks previously known members as non-members when they no longer appear in the API response.
7. Writes a `PlayerSyncRun` row with status and counts.

The looping worker script can be run with:

```bash
sh docker/player_sync.sh
```

In a container, run the worker with the same image and command:

```bash
sh /app/docker/player_sync.sh
```

Set `RUN_MIGRATIONS=0` for the worker service so only the main application container applies migrations.

## Docker

Build the image:

```bash
docker build -t alliance-management .
```

Run with SQLite for a small local/container test:

```bash
mkdir -p data

docker run --rm -it \
  -p 8000:8000 \
  --env-file .env \
  -v "$(pwd)/data:/app/data:rw" \
  alliance-management
```

The runtime image starts Gunicorn on port `8000`. The entrypoint runs migrations by default unless `RUN_MIGRATIONS=0` is set.

The example Compose file in `examples/docker-compose-rootless.yml` shows a production-style layout:

- `management`: web application container
- `player-sync`: separate sync worker container
- `db`: PostgreSQL database
- `traefik-public`: external Traefik network for reverse proxying

Before using the example Compose file, change the image tag, hostnames, Traefik router names, volume paths, and secrets for your own environment. If you use the sync worker, ensure the command points to `/app/docker/player_sync.sh`.

## PostgreSQL example environment

```env
APP_NAME=Alliance Management
DJANGO_SECRET_KEY=replace-with-a-long-random-secret
DJANGO_DEBUG=0
DJANGO_ALLOWED_HOSTS=alliance.example.com
DJANGO_CSRF_TRUSTED_ORIGINS=https://alliance.example.com

DATABASE_ENGINE=postgres
POSTGRES_DB=alliance_management
POSTGRES_USER=alliance_management
POSTGRES_PASSWORD=replace-with-a-strong-password
POSTGRES_HOST=db
POSTGRES_PORT=5432
POSTGRES_CONN_MAX_AGE=60

OIDC_PROVIDER_NAME=OIDC Login
OIDC_CLIENT_ID=your-client-id
OIDC_CLIENT_SECRET=your-client-secret
OIDC_SERVER_URL=https://your-oidc-provider.example.com
OIDC_TOKEN_AUTH_METHOD=client_secret_basic
OIDC_USER_GROUP=server-management
OIDC_ADMIN_GROUP=server-superuser

LASTWAR_TOOLS_BASEURL=https://api.lastwar.tools
LASTWAR_TOOLS_APIKEY=your-api-key
LASTWAR_TOOLS_ALLIANCEID=your-alliance-id

PLAYER_SYNC_INTERVAL_SECONDS=10800
PLAYER_SYNC_INITIAL_DELAY_SECONDS=120
```

## Routes

| Route | Purpose |
|---|---|
| `/healthz/` | Public health check endpoint. Verifies database connectivity. |
| `/login/` | Custom OIDC login start page. |
| `/accounts/` | django-allauth routes. |
| `/` | Alliance dashboard. |
| `/players/` | Current member overview. |
| `/players/?others=true` | Non-member overview. |
| `/players/search/?q=name` | Player search. |
| `/players/{id}` | Player detail page with comments. |
| `/rotation/` | Train conductor rotation page. |
| `/audit-logs/` | Staff-only audit log list. |
| `/admin/` | Django admin. |

Most routes are protected by Django's `LoginRequiredMiddleware`. The login page and health endpoint are intentionally public.

## Notes for contributors and maintainers

- Keep generated JavaScript in sync with TypeScript source by running `task javascript:compile` after frontend changes.
- Run `task check` before opening a pull request.
- Run migrations after model changes with `task django:create-migrations` and `task django:run-migrations`.
- Keep the Taskfile and Docker build strategy aligned. The Taskfile currently uses pnpm; if the Dockerfile uses npm, make sure the matching lockfile exists or adjust the Dockerfile before publishing a release image.
- Do not commit real `.env` files, API keys, OIDC secrets, or database dumps.
- Use strong secrets and HTTPS in production.
- Review `DJANGO_ALLOWED_HOSTS` and `DJANGO_CSRF_TRUSTED_ORIGINS` whenever the deployment domain changes.
- Review OIDC group names before granting access to new users.

## Security and deployment checklist

Before exposing the app outside a private network:

- Set a strong `DJANGO_SECRET_KEY`.
- Set `DJANGO_DEBUG=0`.
- Configure exact `DJANGO_ALLOWED_HOSTS` values.
- Configure exact HTTPS `DJANGO_CSRF_TRUSTED_ORIGINS` values.
- Use HTTPS at the reverse proxy.
- Use PostgreSQL or a properly persisted SQLite volume.
- Back up the database.
- Restrict OIDC access to trusted groups.
- Rotate `OIDC_CLIENT_SECRET` and `LASTWAR_TOOLS_APIKEY` if they were ever exposed.
- Decide how long audit logs and comments should be retained.
- Add monitoring for `/healthz/` and failed `PlayerSyncRun` rows.

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.

## AI disclosure

Parts of this project and its documentation may have been created with assistance from AI tooling. Review generated changes before relying on them in production.
