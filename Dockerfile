FROM python:3.14-slim

RUN apt update

ENV HOST=0.0.0.0
ENV PORT=8000
ENV PYTHONUNBUFFERED=1
ENV VIRTUAL_ENV=/src/.venv
ENV PATH="/src/.venv/bin:$PATH"
ENV POETRY_CACHE_DIR=/tmp/poetry_cache
ENV PYTHON_ARGS="--enable-optimizations --with-tail-call-interp"

WORKDIR /src

# Copy only poetry related files to avoid long rebuild on each file change
COPY ./pyproject.toml /src
COPY ./poetry.lock /src

# Install deps with poetry
RUN pip install poetry && \
    poetry config virtualenvs.create true && \
    poetry config virtualenvs.in-project true && \
    poetry install --no-root --no-interaction --no-ansi

COPY . /src

RUN chmod +x /src/entrypoint.sh
RUN chmod +x /src/.venv/bin/uvicorn

ENTRYPOINT ["./entrypoint.sh"]
