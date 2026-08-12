FROM python:3.12-slim AS builder

ENV PIP_NO_CACHE_DIR=1

WORKDIR /build

COPY requirements.txt .

RUN python -m pip install --upgrade pip \
    && python -m pip wheel \
        --no-cache-dir \
        --wheel-dir /wheels \
        -r requirements.txt


FROM python:3.12-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /srv/app

RUN addgroup --system appgroup \
    && adduser \
        --system \
        --uid 10001 \
        --ingroup appgroup \
        appuser

COPY --from=builder /wheels /wheels
COPY requirements.txt .

RUN python -m pip install \
        --no-cache-dir \
        --no-index \
        --find-links=/wheels \
        -r requirements.txt \
    && rm -rf /wheels

COPY --chown=appuser:appgroup app ./app
COPY --chown=appuser:appgroup migrations ./migrations

USER appuser

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health', timeout=2)" || exit 1

CMD ["gunicorn","--no-control-socket","--bind","0.0.0.0:8000","--workers","2","--threads","2","--timeout","30","app:create_app()"]
