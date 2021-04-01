#!/bin/sh

docker stop $1 > /dev/null
docker rm $1 > /dev/null
time=$(date "+%Y-%m-%d %H:%M:%S")

if sudo docker ps -a --format '{{.Names}}' | grep -Eq "^$1\$"; then
        echo -e "false"
    else
        echo "${time} Deleted $1 Finish" >> ./logs/DeletedDocker
        echo -e "true"
    fi

