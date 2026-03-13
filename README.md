# Backend for Volleyme project

## Prerequisites
1. Use Linux/WSL or MacOS
2. Install docker on [linux](https://docs.docker.com/engine/install/binaries/#install-daemon-and-client-binaries-on-linux) or [macos](https://docs.docker.com/engine/install/binaries/#install-client-binaries-on-macos)
3. Install [docker-compose](https://docs.docker.com/compose/install/linux/#install-using-the-repository)
4. Copy `.sample.env` contents to `.env`
5. (Only for contribution) Install `gcc` compiler
6. (Only for contribution) Install [pyenv](https://github.com/pyenv/pyenv?tab=readme-ov-file#installation)
7. (Only for contribution) Install [poetry](https://python-poetry.org/docs/#installing-with-the-official-installer)


## Project init for local development and debug
1. Install required python version
```bash
pyenv update
pyenv install 3.14
```
2. Initialize virtual environment
```bash
poetry env use 3.14 && poetry config virtualenvs.in-project true && poetry install
```
3. Setup database
```bash
# Up DB
docker-compose up -d postgres
# Run migrations
alembic upgrade head
```
4. You can run server with uvicorn command now
```bash
uvicorn src.volleyme.presentation.rest.main:app --host 0.0.0.0 --port 8000 --reload
```
5. You can find swagger spec on `http://0.0.0.0:8000/docs`
6. (Optional) Copy your IDE config to corresponding folder (`.vscode` or `.idea`)

## Project init using docker

1. Build docker image
```bash
docker-compose build volleyme-backend
```
2. Run migrations
```bash
docker-compose up volleyme-migrate
```
3. Run app, it will run on host/port specified in `.env` file
```bash
docker-compose up volleyme-backend
```
