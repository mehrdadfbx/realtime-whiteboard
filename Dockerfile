FROM python:3.12-slim

# Faster, cleaner Python in containers
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

# Daphne is an ASGI server: it handles both HTTP and WebSocket traffic,
# which plain Gunicorn cannot do on its own.
CMD ["daphne", "-b", "0.0.0.0", "-p", "8000", "whiteboard_project.asgi:application"]
