#!/usr/bin/env bash
source ./bin/env.sh

cd ${PROJECT_HOME}
docker-compose up ${PROJECT_NAME}

echo "======> Running Docker Containers <======="
docker ps --format 'table {{.Names}}\t{{.Image}}\t{{.Command}}\t{{.Status}}'

#docker-bash project