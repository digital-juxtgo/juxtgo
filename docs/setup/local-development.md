# Local Development Setup

## Start system

docker compose up --build

## Stop system

docker compose down

## Access

- App: http://localhost:8000
- DB: localhost:5433

## Services

- web → Django application
- db → PostgreSQL

## Notes

- Web waits for DB before starting
- Migrations run automatically