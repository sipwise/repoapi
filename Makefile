VAR_DIR ?= /var/lib/repoapi
RESULTS ?= ./reports
# do nothing by default
all:

# virtual environments #############
.ONESHELL:
SHELL = /bin/bash
venv_prod: requirements/prod.txt
	virtualenv --python=python3 $(VAR_DIR)/venv_prod
	source $(VAR_DIR)/venv_prod/bin/activate && \
		pip3 install -r ./requirements/prod.txt | tee install.log
###################################

test:
	RESULTS=$(RESULTS) ./manage.py jenkins --enable-coverage --noinput --output-dir $(RESULTS) \
		--settings="repoapi.settings.test"

###################################

deploy: venv_prod
	source $(VAR_DIR)/venv_prod/bin/activate && \
		./manage.py collectstatic --noinput --settings="repoapi.settings.prod"
	chown www-data:www-data -R ./static_media/

migrate: venv_prod
	source $(VAR_DIR)/venv_prod/bin/activate && \
		./manage.py migrate --settings="repoapi.settings.prod"

load_apikeys: venv_prod
	source $(VAR_DIR)/venv_prod/bin/activate && \
		./manage.py loaddata $(VAR_DIR)/apikey.json --settings="repoapi.settings.prod"

shell: venv_prod
	source $(VAR_DIR)/venv_prod/bin/activate && \
		./manage.py shell --settings="repoapi.settings.prod"

###################################

run_dev:
	IP=$(shell ip a show dev eth0 scope global | grep inet | awk '{print $$2}' | cut -d/ -f1); \
	./manage.py runserver_plus $$IP:8000 --settings="repoapi.settings.dev"

worker_dev:
	./manage.py celery worker --loglevel=info --settings="repoapi.settings.dev"

monitor_dev:
	IP=$(shell ip a show dev eth0 scope global | grep inet | awk '{print $$2}' | cut -d/ -f1); \
	./manage.py celery flower --address=$$IP --port=5555 --settings="repoapi.settings.dev"

makemigrations_dev:
	./manage.py makemigrations --settings="repoapi.settings.dev"

migrate_dev:
	./manage.py migrate --settings="repoapi.settings.dev"

shell_dev:
	./manage.py shell --settings="repoapi.settings.dev"
###################################

# get rid of test files
clean:
	find . -type f -name '*.pyc' -exec rm {} \;
	rm -rf reports install.log

# also get rid of virtual environments
distclean dist-clean: clean
	rm -rf venv*

.PHONY: all test clean dist-clean
