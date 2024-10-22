FROM python:3.11.7-bookworm

WORKDIR /app

COPY requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt

COPY .env ./.env
COPY rinha_backend_q1_python ./rinha_backend_q1_python

CMD ["uvicorn", "rinha_backend_q1_python.main:app", "--host", "0.0.0.0", "--port", "8080"]