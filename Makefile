all:

.ONESHELL:
SHELL = /bin/bash
venv_test: requirements/test.txt
	virtualenv --python=python2.7 venv_test
	source ./venv_test/bin/activate && \
		pip install -r ./requirements/test.txt > install.log

.ONESHELL:
SHELL = /bin/bash
venv_dev: requirements/dev.txt
	virtualenv --python=python2.7 venv_dev
	source ./venv_dev/bin/activate && \
		pip install -r ./requirements/dev.txt > install.log


.ONESHELL:
SHELL = /bin/bash
test: venv_test
	export DJANGO_SETTINGS_MODULE="repoapi.settings.dev"
	source ./venv_test/bin/activate && \
	./manage.py jenkins

.ONESHELL:
SHELL = /bin/bash
run_dev: venv_dev
	export DJANGO_SETTINGS_MODULE="repoapi.settings.dev"
	source ./venv_dev/bin/activate && \
		./manage.py runserver_plus

# get rid of test files
clean:
	rm -rf reports install.log

# also get rid of pip environment
dist-clean: clean
	rm -rf venv*

.PHONY: all test clean dist-clean