all:

.ONESHELL:
SHELL = /bin/bash
venv: requeriments/test.txt
	virtualenv --python=python2.7 venv
	source ./venv/bin/activate && \
		pip install -r ./requeriments/test.txt > install.log

test: venv
	source ./venv/bin/activate && \
	./manage.py jenkins

.ONESHELL:
SHELL = /bin/bash
venv_prod: requeriments/prod.txt
	virtualenv --python=python2.7 venv_prod
	source ./venv_prod/bin/activate && \
		pip install -r ./requeriments/prod.txt > install.log

deploy: venv_prod
	mkdir -p ./venv_prod/etc/uwsgi/vassals/
	[ -L ./venv_prod/etc/uwsgi/vassals/repoapi_uwsgi.ini ] || \
		ln -s $(pwd)/repoapi/repoapi_uwsgi.ini ./venv_prod/etc/uwsgi/vassals/

run: deploy
	uwsgi --emperor ./venv_prod/etc/uwsgi/vassals/ --uid www-data --gid www-data

# get rid of test files
clean:
	rm -rf reports install.log

# also get rid of pip environment
dist-clean: clean
	rm -rf venv

.PHONY: all test clean dist-clean