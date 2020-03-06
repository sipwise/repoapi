#!/bin/bash
docker run -d --rm \
	--hostname repoapi-rabbit --name repoapi-rabbit rabbitmq:3
docker pull docker.mgm.sipwise.com/repoapi-buster:latest
docker run --rm -i -t --env=VAR_DIR=/code --link repoapi-rabbit:rabbit \
	-v $(pwd):/code:rw docker.mgm.sipwise.com/repoapi-buster:latest tmux
docker stop repoapi-rabbit
