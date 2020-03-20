#!/bin/bash
repoapi_tag=${1:-latest}
repoapi_image=docker.mgm.sipwise.com/repoapi-buster:${repoapi_tag}

docker run -d --rm \
	--hostname repoapi-rabbit --name repoapi-rabbit rabbitmq:3
docker pull "${repoapi_image}"
docker run --rm -i -t --env=VAR_DIR=/code --link repoapi-rabbit:rabbit \
	-v "$(pwd)":/code:rw "${repoapi_image}" tmux
docker stop repoapi-rabbit
