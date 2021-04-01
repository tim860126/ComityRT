#!/bin/sh
if sudo docker ps -a --format '{{.Names}}' | grep -Eq "^$1\$"; then
        echo -e "true"
    else
        echo -e "false"
    fi
