FROM python:3.10.13-bullseye

COPY poetry.lock pyproject.toml /app/

RUN pip install poetry

WORKDIR /app

RUN python -m poetry install

EXPOSE 5555
