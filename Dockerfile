FROM python:3.11-slim

WORKDIR /app

# System update & install deps
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app
COPY . .

# Expose port & run
EXPOSE 5000
CMD ["python", "app.py"]
