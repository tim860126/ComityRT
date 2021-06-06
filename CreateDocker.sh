#!/bin/sh

docker run -it -d --privileged --cpuset-cpus="$1" --cpus="$3" --memory="$4"m --name=$2 -v /ComityRT/multi-level/$2:/multi-level/$2 tim860126/multi-level:v1 /bin/sh > /dev/null

time=$(date "+%Y-%m-%d %H:%M:%S")

#echo "$1 $2" >> ./logs/CreateDocker
echo "${time} Create $2 Level" >> ./logs/CreateDocker  
