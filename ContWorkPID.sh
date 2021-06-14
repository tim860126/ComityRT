#!/bin/sh
if ps -p $1 > /dev/null
then
  kill -CONT $1
  echo "True"
else
  echo "False"
fi

