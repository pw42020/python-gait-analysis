FROM python:3.10.13-bullseye

WORKDIR /app

RUN pip install poetry

RUN python -m poetry install

WORKDIR /app/src

EXPOSE 5555

CMD ["poetry","run","python", "-m", "zmq_server", "192.168.92.22", "5555"]