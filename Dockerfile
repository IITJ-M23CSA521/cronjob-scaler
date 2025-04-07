FROM python:3.10-slim

WORKDIR /app
COPY scaler.py .
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "scaler.py"]
