#!/bin/sh
if ps -p $1 > /dev/null
then
  kill -9 $1
  echo "True"
else
  echo "False"
fi

