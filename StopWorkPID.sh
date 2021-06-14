#!/bin/sh
if ps -p $1 > /dev/null
then
  kill -STOP $1
  echo "True"
else
  echo "False"
fi

