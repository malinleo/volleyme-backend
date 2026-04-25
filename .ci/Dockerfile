FROM python:3.14-slim AS builder

RUN apt-get update && apt-get install -y --no-install-recommends gcc libc-dev && \
    rm -rf /var/lib/apt/lists/*

ENV POETRY_CACHE_DIR=/tmp/poetry_cache

WORKDIR /src

COPY ./pyproject.toml ./poetry.lock /src/

RUN pip install --no-cache-dir poetry && \
    poetry config virtualenvs.create false && \
    poetry install --no-root --no-interaction --no-ansi --without dev,tests,linters && \
    rm -rf /tmp/poetry_cache

# -----------------------------------------------------------
FROM python:3.14-slim

RUN apt-get update && apt-get install -y --no-install-recommends openssh-client openssl && \
    rm -rf /var/lib/apt/lists/*

ENV HOST=0.0.0.0
ENV PORT=8000
ENV PYTHONUNBUFFERED=1

WORKDIR /src

COPY --from=builder /usr/local/lib/python3.14/site-packages /usr/local/lib/python3.14/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

COPY . /src

RUN chmod +x /src/docker-entrypoint.sh

ENTRYPOINT ["bash", "./docker-entrypoint.sh"]
