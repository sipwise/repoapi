VAR_DIR ?= /var/lib/repoapi

# do nothing by default
all:

# virtual environments #############
.ONESHELL:
SHELL = /bin/bash
venv_test: requirements/test.txt
	virtualenv --python=python2.7 venv_test
	source ./venv_test/bin/activate && \
		pip install -r ./requirements/test.txt | tee install.log

.ONESHELL:
SHELL = /bin/bash
venv_dev: requirements/dev.txt
	virtualenv --python=python2.7 venv_dev
	source ./venv_dev/bin/activate && \
		pip install -r ./requirements/dev.txt | tee install.log

.ONESHELL:
SHELL = /bin/bash
venv_prod: requirements/prod.txt
	virtualenv --python=python2.7 $(VAR_DIR)/venv_prod
	source $(VAR_DIR)/venv_prod/bin/activate && \
		pip install -r ./requirements/prod.txt | tee install.log
###################################

test: venv_test
	source ./venv_test/bin/activate && \
		./manage.py jenkins --settings="repoapi.settings.dev"

deploy: venv_prod
	source $(VAR_DIR)/venv_prod/bin/activate && \
		./manage.py collectstatic --noinput --settings="repoapi.settings.prod"
	chown www-data:www-data -R ./static_media/

migrate: venv_prod
	source $(VAR_DIR)/venv_prod/bin/activate && \
		./manage.py migrate --settings="repoapi.settings.prod"
	chown www-data:www-data $(VAR_DIR)/db.sqlite3

###################################

run_dev: venv_dev
	source ./venv_dev/bin/activate && \
		./manage.py runserver_plus --settings="repoapi.settings.dev"

###################################

# get rid of test files
clean:
	find . -type f -name '*.pyc' -exec rm {} \;
	rm -rf reports install.log

# also get rid of virtual environments
distclean dist-clean: clean
	rm -rf venv*

.PHONY: all test clean dist-clean