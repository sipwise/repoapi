# DOCKER_NAME=repoapi-trixie
FROM docker.mgm.sipwise.com/sipwise-trixie:latest

# Important! Update this no-op ENV variable when this Dockerfile
# is updated with the current date. It will force refresh of all
# of the base images and things like `apt-get update` won't be using
# old cached versions when the Dockerfile is built.
ENV REFRESHED_AT=2026-11-11

RUN apt-get update && \
    apt-get install --assume-yes \
      git \
      iproute2 \
      pycodestyle \
      python3 \
      python3-dev \
      python3-junitxml \
      python3-pip \
      python3-pytest \
      python3-pytest-cov \
      python3-pytest-pylint \
      python3-venv \
      sqlite3 \
      tmux \
      && \
    apt-get clean

# Get pip to download and install requirements:
ADD requirements/*.txt /tmp/
RUN pip3 install --break-system-packages -r /tmp/test.txt

RUN echo './t/testrunner' >>/root/.bash_history
ADD .tmux.conf /root/.tmux.conf

WORKDIR /code/

################################################################################
# Instructions for usage
# ----------------------
# When you want to build the base image from scratch (jump to the next section if you don't want to build yourself!):
# % docker build --tag="repoapi-trixie" -f t/Dockerfile .
# % docker run --rm -i -t -v $(pwd):/code:rw repoapi-trixie:latest bash
#
# Use the existing docker image:
# % docker pull docker.mgm.sipwise.com/repoapi-trixie
# % docker run --rm -i -t -v $(pwd):/code:rw docker.mgm.sipwise.com/repoapi-trixie:latest bash
#
# Inside docker (the command is in history, just press UP button):
#   ./t/testrunner
#
# Run django inside docker:
# see README.md
################################################################################
