# flask-app-template

Simple [Flask](http://flask.pocoo.org/) application template for HTTP API backend
with decoupled business logic,
[Alembic](http://alembic.zzzcomputing.com/en/latest/),
[pytest](https://docs.pytest.org/en/latest/),
[uWSGI](https://uwsgi-docs.readthedocs.io/en/latest/),
[Sentry](https://sentry.io/),
[statsd server](https://github.com/baverman/statsdly/) and docker.


## Features

* Clean architecture. Flask `request`/`app` objects are limited to `web` package
  only. It narrows possibilities for deep penetration of framework and HTTP layer into
  an aplication core and leads to better design.

* Ready to use API routes with errors and fast json serialization.

* Fast start, you only need to replace `my_project` occurrences and ready to
  code models and endpoints.

* Alembic migrations.

* Configured pytest with dbsession fixture to prepare tables for your
  unit tests.

* Sentry integration.

* Graphite/Carbon/Grafana integration.

* Flexible configuration.

* Multistage dockerfiles (gcc, dev libs and other tooling are stripped).
  Alpine by default with Ubuntu as alternative.

* Ready to deploy to production. Without serious scalability in mind, because it's
  a DevOps work anyway.


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


## Deploy to some docker-aware server

You need ssh login to host and working docker environment there also
you need locally installed Fabric3. For first deploy run:

    fab -H some.host init push_image upload migrate restart

Following deploys need:

    fab -H some.host upload restart

If you changed `docker/Dockerfile.*` or `requirements.txt` you should update
image on a server:

    fab -H some.host push_image

You can tune default host, http port and config file location in `fabfile.py`.
For full list of commands you can run `fab --list`.
