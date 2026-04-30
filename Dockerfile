FROM python:3.11-slim

# Install nginx and supervisor
RUN apt-get update && apt-get install -y --no-install-recommends nginx supervisor \
    && rm -rf /var/lib/apt/lists/*

# ── Backend ──
WORKDIR /app/backend
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY backend/ .

# ── Frontend ──
COPY frontend/ /usr/share/nginx/html/

# ── Config files ──
COPY deploy/nginx.conf /etc/nginx/sites-available/default
COPY deploy/supervisord.conf /etc/supervisor/conf.d/app.conf
COPY deploy/start.sh /app/start.sh
RUN chmod +x /app/start.sh

# Persistent DB lives here (mount a volume to /data)
RUN mkdir -p /data

# Fix nginx pid path so it doesn't conflict
RUN sed -i 's|/run/nginx.pid|/tmp/nginx.pid|' /etc/nginx/nginx.conf

VOLUME ["/data"]

EXPOSE 8080

CMD ["/app/start.sh"]
