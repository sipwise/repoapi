repoapi
===========

interface to manage our debian repositories metadata


go away! This is on pre-alpha^4 development stage.


Devel environment
=================
$ make venv_dev
$ source ./venv_dev/bin/activate

Create DB
=========
(repoapi)$ ./manage.py migrate

Create superuser
================
(repoapi)$ ./manage.py createsuperuser

Run test server
================
(repoapi)$ ./manage.py runserver_plus

Tests
=====
(repoapi)$ ./manage.py test

Reports
=======
(repoapi)$ ./manage.py jenkins
