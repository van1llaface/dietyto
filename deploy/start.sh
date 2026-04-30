#!/bin/bash
# Seed only if database doesn't exist yet (first run)
if [ ! -f /data/longevity.db ]; then
    echo "First run — seeding database..."
    cd /app/backend && python seed.py
    cp /app/backend/longevity.db /data/longevity.db
fi

# Symlink so the app reads from the persistent volume
ln -sf /data/longevity.db /app/backend/longevity.db

# Run migrations (adds any new columns/tables safely)
cd /app/backend && DB_PATH=/data/longevity.db python migrate.py

# Start supervisor (nginx + uvicorn)
exec supervisord -c /etc/supervisor/supervisord.conf
