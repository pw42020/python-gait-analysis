FROM python:3.10.13-bullseye

COPY .. /app

WORKDIR /app

RUN pip install poetry

RUN python -m poetry install

WORKDIR /app/src

EXPOSE 5555

CMD ["python", "-m", "zmq_server", "127.0.0.1", "5555"]