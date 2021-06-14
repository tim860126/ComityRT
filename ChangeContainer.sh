#!/bin/sh

cID=$(docker inspect -f '{{.ID}}' $1)
#WPID=$(pidof $2)
if ps -p $2 > /dev/null
then
  WPID=$2
  echo "${time} PID ${WPID} level: $1 work $2" >> ./Change
  echo ${WPID} >> /sys/fs/cgroup/hugetlb/system.slice/docker-${cID}.scope/tasks
  echo ${WPID} >> /sys/fs/cgroup/cpuset/system.slice/docker-${cID}.scope/tasks
  echo ${WPID} >> /sys/fs/cgroup/blkio/system.slice/docker-${cID}.scope/tasks
  echo ${WPID} >> /sys/fs/cgroup/pids/system.slice/docker-${cID}.scope/tasks
  echo ${WPID} >> /sys/fs/cgroup/devices/system.slice/docker-${cID}.scope/tasks
  echo ${WPID} >> /sys/fs/cgroup/cpuset/system.slice/docker-${cID}.scope/tasks
  echo ${WPID} >> /sys/fs/cgroup/perf_event/system.slice/docker-${cID}.scope/tasks
  echo ${WPID} >> /sys/fs/cgroup/net_prio/system.slice/docker-${cID}.scope/tasks
  echo ${WPID} >> /sys/fs/cgroup/net_cls/system.slice/docker-${cID}.scope/tasks
  echo ${WPID} >> /sys/fs/cgroup/memory/system.slice/docker-${cID}.scope/tasks
  echo ${WPID} >> /sys/fs/cgroup/cpuacct/system.slice/docker-${cID}.scope/tasks
  echo ${WPID} >> /sys/fs/cgroup/cpu/system.slice/docker-${cID}.scope/tasks
  echo ${WPID} >> /sys/fs/cgroup/systemd/system.slice/docker-${cID}.scope/tasks
  echo ${WPID} >> /sys/fs/cgroup/freezer/system.slice/docker-${cID}.scope/tasks
else
  echo "${time} PID Error level: $1 work $2" >> ./Change
fi
