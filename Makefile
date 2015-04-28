# do nothing by default
all:

# virtual environments #############
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
venv_prod: requirements/prod.txt
	virtualenv --python=python2.7 venv_prod
	source ./venv_prod/bin/activate && \
		pip install -r ./requirements/prod.txt > install.log
###################################

test: venv_test
	source ./venv_test/bin/activate && \
		./manage.py jenkins --settings="repoapi.settings.dev"

deploy: venv_prod
	mkdir -p ./venv_prod/etc/uwsgi/vassals/
	[ -L ./venv_prod/etc/uwsgi/vassals/repoapi_uwsgi.ini ] || \
		ln -s $(shell pwd)/repoapi/repoapi_uwsgi.ini \
			./venv_prod/etc/uwsgi/vassals/
	touch ./venv_prod/etc/uwsgi/vassals/repoapi_uwsgi.ini
	chown jenkins:www-data -R ./venv_prod/etc/uwsgi
	source ./venv_prod/bin/activate && \
		./manage.py collectstatic --noinput --settings="repoapi.settings.prod"
	chown jenkins:www-data -R ./static_media/ && chmod 660 -R ./static_media/
	touch /var/log/uwsgi-repoapi.log && \
		chown jenkins:www-data /var/log/uwsgi-repoapi.log && \
		chmod 664 /var/log/uwsgi-repoapi.log

###################################

run_dev: venv_dev
	source ./venv_dev/bin/activate && \
		./manage.py runserver_plus --settings="repoapi.settings.dev"

run: deploy
	mkdir -p ./venv_prod/run
	chown jenkins:www-data ./venv_prod/run && chmod 770 ./venv_prod/run
	source ./venv_prod/bin/activate && \
		uwsgi --emperor ./venv_prod/etc/uwsgi/vassals/ \
			--uid www-data --gid www-data

###################################

# get rid of test files
clean:
	rm -rf reports install.log

# also get rid of virtual environments
dist-clean: clean
	rm -rf venv*

.PHONY: all test clean dist-clean