#!/usr/bin/env bash

echo -e "Setting envs from './bin/env.sh'...\n"
source ./bin/env.sh
echo -e "********** ENVIRONMENT VARIABLES begins **********\n"
# value=$(eval "echo \"$(cat ./bin/env.sh)\"")
value=`eval echo \"$(cat ./bin/env.sh)\"`
export_vars=""
for i in $value
do
    [[ $i = "export" ]] && : || export_vars+=$(echo "$(echo "$i" | awk -F= '{print $1}')|")
done
printenv | grep -E "${export_vars}::-1}" | column -t -s "="
echo -e "\n********** ENVIRONMENT VARIABLES ends ************\n"

cd ${PROJECT_HOME}
docker-compose build ${PROJECT_NAME}
