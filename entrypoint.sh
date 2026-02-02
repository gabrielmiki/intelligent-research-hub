#!/bin/sh

# Exit immediately if a command exits with a non-zero status
set -e

# 1. Run Migrations
# (Ideally, you run this in a separate release phase, but for Docker Compose, it's fine here)
echo "Applying database migrations..."
python manage.py migrate --noinput

# 2. Collect Static Files
# This puts all CSS/JS into the /app/static folder, which Nginx reads via the volume
echo "Collecting static files..."
python manage.py collectstatic --noinput

# 3. Create a default Superuser (Optional - convenient for dev/portfolio)
# python manage.py createsuperuser --noinput || true

# 4. Execute the command passed to the docker container (Start Gunicorn)
echo "Starting Server..."
exec "$@"