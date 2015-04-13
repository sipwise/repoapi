all:

.ONESHELL:
SHELL = /bin/bash
venv: requeriments/dev.txt
	virtualenv --python=python2.7 venv
	source ./venv/bin/activate && \
		pip install -r ./requeriments/dev.txt > install.log

test: venv
	source ./venv/bin/activate && \
	./manage.py jenkins

# get rid of test files
clean:
	rm -rf reports install.log

# also get rid of pip environment
dist-clean: clean
	rm -rf venv

.PHONY: all test clean dist-clean