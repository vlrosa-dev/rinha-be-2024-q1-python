FROM python:3.11-buster

RUN pip install poetry==1.4.2

WORKDIR /app

COPY pyproject.toml poetry.lock ./
COPY rinha_backend_q1_python ./rinha_backend_q1_python

RUN poetry install --without dev

ENTRYPOINT ["poetry", "run", "python", "-m", "rinha_backend_q1_python.main"]