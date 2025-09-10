FROM python:3.11-slim

WORKDIR /app

# Copy requirements and install
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . /app

CMD ["python", "slack_status.py"]
