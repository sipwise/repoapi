repoapi
=======

interface to manage our Debian repositories metadata.

go away! This is on pre-alpha^4 development stage.

Run docker containers
---------------------

    $ docker run --rm --hostname repoapi-rabbit --name repoapi-rabbit rabbitmq:3
    $ docker run --rm -i -t --link repoapi-rabbit:rabbit -v $(pwd):/code:rw docker.mgm.sipwise.com/repoapi-buster:latest bash

Prepare development environment
===============================

On your desktop, install pre-commit tool

[pre-commit](https://pre-commit.com/)
-------------------------------------

  * apt install build-essential python3-dev python3-virtualenvwrapper virtualenvwrapper
  * mkvirtualenv repos-scritps --python=python3
  * pip3 install pre-commit
  * pre-commit install

Inside the repoapi-buster container run:

    $ export VAR_DIR=/tmp/repoapi
    $ make venv_dev
    $ source ${VAR_DIR}/venv_dev/bin/activate

Create DB
=========

To ensure `db.sqlite3` exists as needed:

    (repoapi)$ ./manage.py migrate --settings="repoapi.settings.dev"

Create superuser
================

    (repoapi)$ ./manage.py createsuperuser --settings="repoapi.settings.dev"

Run test server
================

If you want to run it on a specific IP, use:

    (repoapi)$ IP=172.17.0.3 # adjust as needed
    (repoapi)$ ./manage.py runserver_plus $IP:8000 --settings="repoapi.settings.dev"

or just:

    (repoapi)$  make run_dev

Tests
=====

    (repoapi)$ ./manage.py test

Reports
=======

    (repoapi)$ ./manage.py jenkins
