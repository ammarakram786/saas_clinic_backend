[database]
ENGINE=django.db.backends.postgresql
NAME=wim
USER=postgres
PASSWORD=postgres
HOST=localhost
PORT=5432

[urls]
TRUSTED_ORIGINS=http://localhost:8080,http://localhost:8000
CORS_ORIGINS=http://localhost:8080,http://localhost:8000
ALLOWED_HOSTS =localhost


[redis]
HOST=127.0.0.1
PORT=6379
DB=0

