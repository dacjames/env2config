#!/bin/sh

if [ "$1" = 'redis-server' ]; then
    env2config inject /default_configs
    exec "$@"
fi

exec "$@"
