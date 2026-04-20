"""Development settings."""
from .base import *  # noqa: F401,F403
from .base import env


DEBUG = True

# Allow sqlite override for quick local work if DATABASE_URL isn't set
# to a real Postgres DSN. Postgres is still the real default via base.py.
_sqlite_override = env('SQLITE_PATH', default=None)
if _sqlite_override:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': _sqlite_override,
        }
    }
