FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY src/ src/
COPY src/bloggy/templates/ templates/

CMD ["python", "-m", "src.bloggy.app"]