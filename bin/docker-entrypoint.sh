#!/bin/sh

env2config inject /default_configs

exec "$@"
