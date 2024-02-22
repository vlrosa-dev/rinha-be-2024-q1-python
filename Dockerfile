FROM python:3.11-buster

WORKDIR /app

COPY requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt

COPY rinha_backend_q1_python ./rinha_backend_q1_python

CMD ["uvicorn", "rinha_backend_q1_python.main:app", "--host", "0.0.0.0", "--port", "8000"]

#ENTRYPOINT ["python", "-m", "rinha_backend_q1_python.main"]