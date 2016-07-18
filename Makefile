VAR_DIR ?= /var/lib/repoapi
RESULTS ?= ./reports
# do nothing by default
all:

# virtual environments #############
.ONESHELL:
SHELL = /bin/bash
venv_prod: requirements/prod.txt
	virtualenv --python=python2.7 $(VAR_DIR)/venv_prod
	source $(VAR_DIR)/venv_prod/bin/activate && \
		pip install -r ./requirements/prod.txt | tee install.log
###################################

test:
	./manage.py jenkins --enable-coverage --noinput --output-dir $(RESULTS) \
		--settings="repoapi.settings.dev"

deploy: venv_prod
	source $(VAR_DIR)/venv_prod/bin/activate && \
		./manage.py collectstatic --noinput --settings="repoapi.settings.prod"
	chown www-data:www-data -R ./static_media/

migrate: venv_prod
	source $(VAR_DIR)/venv_prod/bin/activate && \
		./manage.py migrate --settings="repoapi.settings.prod"
	chown www-data:www-data $(VAR_DIR)/db.sqlite3

###################################

run_dev:
	IP=$(shell ip a show dev eth0 scope global | grep inet | awk '{print $$2}' | cut -d/ -f1); \
	./manage.py runserver_plus $$IP:8000 --settings="repoapi.settings.dev"

worker_dev:
	DJANGO_SETTINGS_MODULE="repoapi.settings.dev" \
		celery -A repoapi worker --loglevel=info

###################################

# get rid of test files
clean:
	find . -type f -name '*.pyc' -exec rm {} \;
	rm -rf reports install.log

# also get rid of virtual environments
distclean dist-clean: clean
	rm -rf venv*

.PHONY: all test clean dist-clean