# DOCKER_NAME=repoapi-bullseye
FROM docker.mgm.sipwise.com/sipwise-bullseye:latest

# Important! Update this no-op ENV variable when this Dockerfile
# is updated with the current date. It will force refresh of all
# of the base images and things like `apt-get update` won't be using
# old cached versions when the Dockerfile is built.
ENV REFRESHED_AT 2022-07-06

RUN apt-get update && apt-get install --assume-yes python3 python3-dev \
	python3-pytest python3-pytest-pep8 \
	python3-pytest-pylint python3-pytest-cov python3-junitxml \
	python3-pip python3-virtualenv virtualenv sqlite3 git tmux

# Get pip to download and install requirements:
ADD requirements/*.txt /tmp/
RUN pip3 install -r /tmp/test.txt

RUN echo './t/testrunner' >>/root/.bash_history
ADD .tmux.conf /root/.tmux.conf
RUN apt-get clean

WORKDIR /code/

################################################################################
# Instructions for usage
# ----------------------
# When you want to build the base image from scratch (jump to the next section if you don't want to build yourself!):
# % docker build --tag="repoapi-bullseye" -f t/Dockerfile .
# % docker run --rm -i -t -v $(pwd):/code:rw repoapi-bullseye:latest bash
#
# Use the existing docker image:
# % docker pull docker.mgm.sipwise.com/repoapi-bullseye
# % docker run --rm -i -t -v $(pwd):/code:rw docker.mgm.sipwise.com/repoapi-bullseye:latest bash
#
# Inside docker (the command is in history, just press UP button):
#   ./t/testrunner
#
# Run django inside docker:
# see README.md
################################################################################
