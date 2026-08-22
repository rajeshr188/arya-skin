FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim AS builder

ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy
WORKDIR /app

RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-install-project --no-dev

COPY . /app
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev
RUN DJANGO_DEBUG=False \
    SECRET_KEY=container-build-only-not-for-runtime-12345678901234567890 \
    /app/.venv/bin/python manage.py collectstatic --noinput

FROM python:3.12-slim-bookworm

RUN addgroup --system app && adduser --system --ingroup app app
COPY --from=builder --chown=app:app /app /app

WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PATH="/app/.venv/bin:$PATH"

RUN mkdir -p /app/media && \
    chown app:app /app/media && \
    chmod +x /app/scripts/release.sh
USER app

EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
    CMD python -c "import os, urllib.request; port=os.environ.get('PORT', '8000'); host=os.environ.get('HEALTH_CHECK_HOST', 'localhost'); request=urllib.request.Request(f'http://127.0.0.1:{port}/healthz/', headers={'Host': host}); urllib.request.urlopen(request, timeout=3)"

CMD ["gunicorn", "--config", "gunicorn.conf.py", "django_project.wsgi"]
