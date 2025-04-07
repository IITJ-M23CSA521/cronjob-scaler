# Dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY scaler.py .

RUN pip install requests kubernetes

CMD ["python", "scaler.py"]
