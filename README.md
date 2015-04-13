repoapi
===========

interface to manage our debian repositories metadata


go away! This is on pre-alpha^4 development stage.


Devel environment
=================
$ mkvirtualenv repoapi

(repoapi)$ pip install -r requeriments/dev.txt

(repoapi)$ nodeenv --requirement=requeriments/npm-dev.txt ~/.virtualenvs/repoapi/npm

(repoapi)$ . ~/.virtualenvs/repoapi/npm/bin/activate

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
