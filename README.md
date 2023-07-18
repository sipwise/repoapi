repoapi
=======

interface to manage our Debian repositories metadata.

go away! This is on pre-alpha^4 development stage.

Run docker containers
---------------------

    $ docker run -d --rm --hostname repoapi-rabbit --name repoapi-rabbit rabbitmq:3
    $ docker run --rm -i -t --link repoapi-rabbit:rabbit -v $(pwd):/code:rw docker.mgm.sipwise.com/repoapi-bullseye:latest bash

Tmux
----

Use tmux inside repoapi-buster container so you can execute both dev server and worker

```
$ docker run --rm -i -t --link repoapi-rabbit:rabbit --env=VAR_DIR=/code -v $(pwd):/code:rw docker.mgm.sipwise.com/repoapi-buster:latest tmux
```
or just execute ``./tmux.sh``

Prepare development environment
===============================

On your desktop, install pre-commit tool

[pre-commit](https://pre-commit.com/)
-------------------------------------

  * sudo apt install build-essential python3-dev npm
  * sudo npm install -g eslint
  * npm install eslint-config-jquery
  * sudo apt install pre-commit || pip3 install pre-commit
  * pre-commit install

virtualenv
----------

Inside the repoapi container run:

```
  $ make venv_dev
  $ source $(VAR_DIR)/venv_dev/bin/activate
  (venv_dev)$
```

Create DB
---------

To ensure `db.sqlite3` exists as needed:

  ```
  (venv_dev)$ ./manage.py migrate --settings="repoapi.settings.dev"
  ```
  or
  ```
  $ make migrate_dev
  ```

Create superuser
----------------

  ```
  (venv_dev)$ ./manage.py createsuperuser --settings="repoapi.settings.dev"
  ```


Run dev server
--------------

If you want to run it on a specific IP, use:

  ```
  (venv_dev)$ IP=172.17.0.3 # adjust as needed
  (venv_dev)$ ./manage.py runserver_plus $IP:8000 --settings="repoapi.settings.dev"
  ```
or just:
  ```
  $ make run_dev
  ```

Run dev worker
--------------

```
  $ make worker_dev
```

Tests
-----

```
  (venv_dev)$ ./manage.py test
```

Reports
-------

```
  (venv_dev)$ ./manage.py jenkins
```
