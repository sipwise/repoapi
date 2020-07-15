#!/bin/bash
dfile=$(dirname "$0")/t/Dockerfile
repoapi_tag=${1:-latest}
docker_name=$(sed -ne 's/^# DOCKER_NAME=\(.\+\)$/\1/p;Tn;q;:n' "${dfile}" || true)
repoapi_image=docker.mgm.sipwise.com/${docker_name}:${repoapi_tag}

docker run -d --rm \
	--hostname repoapi-rabbit --name repoapi-rabbit rabbitmq:3
docker pull "${repoapi_image}"
docker run --rm -i -t --env=VAR_DIR=/code --link repoapi-rabbit:rabbit \
	-v "$(pwd)":/code:rw "${repoapi_image}" tmux
docker stop repoapi-rabbit
