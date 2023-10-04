FROM python:3.10.13-bullseye

# install poetry

COPY .. /app

WORKDIR /app

RUN pip install poetry

RUN python -m poetry install

WORKDIR /app/src

EXPOSE 5555

CMD ["poetry","run","python", "-m", "analyze_gait", "zmqserver", "5555"]
