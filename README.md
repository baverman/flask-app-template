# flask-app-template

Simple flask application template for HTTP API backend with decoupled business logic, alembic, pytest,
sentry, statsd server and docker.


## Local run in virtualenv

1. Your favourite way to make virtualenv. (I like
   [virtualenvwrapper](https://virtualenvwrapper.readthedocs.io/en/latest/)).

1. Install python requirements:

       pip install -r requirements.txt -r requirements-dev.txt

1. Run migrations:

       alembic upgrade head

1. Run server:

       uwsgi --ini etc/uwsgi.ini --py-autoreload=2

1. Call some endpoints:

       curl -X POST 127.0.0.1:5000/add?value=10
       curl -X POST 127.0.0.1:5000/add?value=10
       curl -X GET 127.0.0.1:5000/sum

1. Run tests:

       py.test


## Local run with docker-compose

1. Build image:

       ./docker/build.sh

   You can use multi-stage dockerfiles for newer (>= 17.03) docker runtimes. See docker directory.
   By default template assumes "legacy" versions and emulates multi-stage build via special
   script.

1. Run migrations:

      USER_ID=$UID:$GROUPS docker-compose run http alembic upgrade head

1. Run server:

      USER_ID=$UID:$GROUPS docker-compose up

1. Call some endpoints:

       curl -X POST 127.0.0.1:5000/add?value=10
       curl -X POST 127.0.0.1:5000/add?value=10
       curl -X GET 127.0.0.1:5000/sum


## Deploy to some docker aware server

You need installed Fabric3. For first deploy run:

    fab -H some.host init push_image upload migrate restart

Following deploys need:

    fab -H some.host upload restart

If you changed `docker/Dockerfile.*` or `requirements.txt` you should update
image on a server:

    fab -H some.host push_image

You can tune default host, http port and config file location in `fabfile.py`.
