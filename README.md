# opct-backend

OPCT comes from `Operation Program Change Tracker`. Web app to track operation program changes.

## Dev environment

### Requirements

- Python 3
- Dependencies: requirements.txt

## Configuration

It's recommended to use a virtual environment to keep dependencies required by different projects separate by creating isolated python virtual environments for them.

To create a virtual environment:

```
virtualenv venv
```
If you are using Python 2.7 by default is needed to define a Python3 flag:

```
virtualenv -p python3 venv
```

Activate virtual env and install dependencies:
```
source venv/bin/activate
 
pip install -r requirements.txt
```

### .env file
The env files allow you to put your environment variables inside a file, it is recommended to only have to worry once about the setup and configuration of application and to not store passwords and sensitive data in public repository.
 
You need to define the environment keys creating an .env file at root path:

```
# you can create a key here: https://miniwebtool.com/es/django-secret-key-generator/
SECRET_KEY=key

DEBUG=True

ALLOWED_HOSTS=127.0.0.1,localhost

# Postgres parameters
DB_NAME=db_name
DB_USER=db_user_name
DB_PASS=db_user_pass
DB_HOST=localhost
DB_PORT=5432

# needed in dev mode
CORS_ALLOWED_ORIGINS=http://localhost:8080

# Redis parameters
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0

EMAIL_HOST=
EMAIL_PORT=
EMAIL_USE_TLS=
EMAIL_HOST_USER=
EMAIL_HOST_PASSWORD=
SERVER_EMAIL=
DEFAULT_FROM_EMAIL=
```

### Load fixtures 
To initialize the database, you need to load the fixtures.

```
loaddata contracttypes operationprogramstatuses operationprogramtypes groups grouppermissions changeoprequeststatuses changeopprocessstatuses
```
## Test

Run test with:
```
python manage.py test
```

# Docker

## Build image

```
docker build -f docker\Dockerfile -t opct .
```

## Build and run docker-compose

### development mode

Build command:
```
docker-compose -p opct -f docker\docker-compose.yml -f docker\docker-compose.dev.yml build --build-arg GIT_PERSONAL_TOKEN=<git_personal_token>
```

Run command:
```
docker-compose -p opct -f docker\docker-compose.yml -f docker\docker-compose.dev.yml up
```

Stop command:
```
docker-compose -p opct -f docker\docker-compose.yml -f docker\docker-compose.dev.yml down
```

Sometimes you want to update frontend code without upgrade everything else, so in these cases you should call:
```
docker-compose -p opct -f docker\docker-compose.yml -f docker\docker-compose.dev .yml build --build-arg GIT_PERSONAL_TOKEN=<git_personal_token> --no-cache nginx
```

### production mode

Build command:
```
docker-compose -p opct -f docker\docker-compose.yml -f docker\docker-compose.prod.yml build --build-arg GIT_PERSONAL_TOKEN=<git_personal_token>
```

Run command:
```
docker-compose -p opct -f docker\docker-compose.yml -f docker\docker-compose.prod.yml up
```

Stop command:
```
docker-compose -p opct -f docker\docker-compose.yml -f docker\docker-compose.prod.yml down
```

Sometimes you want to update frontend code without upgrade everything else, so in these cases you should call:
```
docker-compose -p opct -f docker\docker-compose.yml -f docker\docker-compose.prod .yml build --build-arg GIT_PERSONAL_TOKEN=<git_personal_token> --no-cache nginx
```