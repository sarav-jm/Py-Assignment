#!/usr/bin/env bash

source ./bin/env.sh

cd ${PROJECT_HOME}
docker-compose stop

echo "======> Running Docker Containers <======="
docker ps
