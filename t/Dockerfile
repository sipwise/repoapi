# DOCKER_NAME=repoapi-stretch
FROM docker.mgm.sipwise.com/sipwise-stretch:latest

# Important! Update this no-op ENV variable when this Dockerfile
# is updated with the current date. It will force refresh of all
# of the base images and things like `apt-get update` won't be using
# old cached versions when the Dockerfile is built.
ENV REFRESHED_AT 2017-07-21

RUN apt-get update
RUN apt-get install --assume-yes python3 python3-dev \
	python3-pip git screen

# Get pip to download and install requirements:
ADD requirements/*.txt /tmp/
RUN pip3 install -r /tmp/test.txt

RUN echo './t/testrunner' >>/root/.bash_history

RUN apt-get clean

WORKDIR /code/

################################################################################
# Instructions for usage
# ----------------------
# When you want to build the base image from scratch (jump to the next section if you don't want to build yourself!):
# % docker build --tag="repoapi-stretch" -f t/Dockerfile .
# % docker run --rm -i -t -v $(pwd):/code:rw repoapi-stretch:latest bash
#
# Use the existing docker image:
# % docker pull docker.mgm.sipwise.com/repoapi-stretch
# % docker run --rm -i -t -v $(pwd):/code:rw docker.mgm.sipwise.com/repoapi-stretch:latest bash
#
# Inside docker (the command is in history, just press UP button):
#   ./t/testrunner
#
# Run django inside docker:
# % pip3 install -r requirements/dev.txt && make run_dev
#
# We need a working rabbit server, so in another terminal:
# % docker run --rm --hostname repoapi-rabbit --name repoapi-rabbit rabbitmq:3
# and link both containers:
# % docker run --rm -i -t --link repoapi-rabbit:rabbit -v $(pwd):/code:rw docker.mgm.sipwise.com/repoapi-stretch:latest bash
#
# use screen to get a working worker in the background:
# % make worker_dev
################################################################################
