# syntax=docker/dockerfile:1

FROM node:24-slim AS frontend-builder

WORKDIR /app

RUN corepack enable

COPY package.json pnpm-lock.yaml ./
RUN pnpm install --frozen-lockfile

COPY tsconfig.json ./
COPY typescript ./typescript
RUN pnpm run build:ts


FROM ghcr.io/astral-sh/uv:python3.13-trixie-slim AS builder

ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy
ENV UV_PROJECT_ENVIRONMENT=/app/.venv

WORKDIR /app

COPY pyproject.toml uv.lock ./
RUN uv sync --locked --no-dev --no-install-project

COPY . .
COPY --from=frontend-builder /app/core/static/core/js ./core/static/core/js
RUN uv sync --locked --no-dev

# collectstatic needs Django settings to import successfully
RUN DJANGO_DEBUG=0 DJANGO_SECRET_KEY=build-time-secret uv run python manage.py collectstatic --noinput


FROM python:3.14-slim-trixie AS runtime

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PATH="/app/.venv/bin:$PATH"

WORKDIR /app

RUN addgroup --gid 10001 --system django \
    && adduser --uid 10001 --system --ingroup django --home /home/django django

COPY --from=builder /app /app

RUN chmod +x /app/docker/*.sh \
    && chown -R django:django /app

USER django

ENV RUNNING_IN_CONTAINER true

EXPOSE 8000

ENTRYPOINT ["/app/docker/entrypoint.sh"]

CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3", "--access-logfile", "-", "--error-logfile", "-", "--no-control-socket"]
