#!/bin/sh

docker run -it -d --privileged --cpuset-cpus $1 --name $2 \
           -v /ComityRT/multi-level/$2:/multi-level/$2 tim860126/multi-level:v1 /bin/sh > /dev/null

time=$(date "+%Y-%m-%d %H:%M:%S")
echo "${time} Create $2 Level" >> ./logs/CreateDocker  
