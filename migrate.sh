#!/bin/sh

docker-compose -f docker-compose.yml up -d --build --v
docker-compose -f docker-compose.yml exec web python manage.py migrate --noinput
docker-compose -f docker-compose.yml exec web python manage.py loaddata db.json
docker-compose -f docker-compose.yml exec web python manage.py collectstatic --no-input --clear

exec "$@"