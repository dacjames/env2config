# env2config

`env2config` is a simple utility for generating configuration files that allows environment variables to override vendor-provided defaults.  It is primarily designed for use with containerization technologies like [Docker](https://www.docker.com/) and can be easily extended to support new configuration file formats.

## Usage

```sh
dcollinsⓔenv2config:~$ env2config build redis 3.0.1 ./default_configs
dcollinsⓔenv2config:~$ tree ./default_configs
./default_configs
└── redis
    └── 3.0.1
        └── redis.conf

2 directories, 1 file
dcollinsⓔenv2config:~$ cat ./default_configs/redis/3.0.1/redis.conf \
                            | grep -B 20 'appendonly'
############################## APPEND ONLY MODE ###############################

# By default Redis asynchronously dumps the dataset on disk. This mode is
# good enough in many applications, but an issue with the Redis process or
# a power outage may result into a few minutes of writes lost (depending on
# the configured save points).
#
# The Append Only File is an alternative persistence mode that provides
# much better durability. For instance using the default data fsync policy
# (see later in the config file) Redis can lose just one second of writes in a
# dramatic event like a server power outage, or a single write if something
# wrong with the Redis process itself happens, but the operating system is
# still running correctly.
#
# AOF and RDB persistence can be enabled at the same time without problems.
# If the AOF is enabled on startup Redis will load the AOF, that is the file
# with the better durability guarantees.
#
# Please check http://redis.io/topics/persistence for more information.

appendonly no
--

# The name of the append only file (default: "appendonly.aof")
--
## NOTE: '-' is a special "path", meaning stdout
dcollinsⓔenv2config:~$ env REDIS_INJECT='redis.conf:-' \
                            REDIS_APPENDONLY=yes \
                            env2config inject ./default_configs \
                            | grep -B 20 appendonly
############################## APPEND ONLY MODE ###############################

# By default Redis asynchronously dumps the dataset on disk. This mode is
# good enough in many applications, but an issue with the Redis process or
# a power outage may result into a few minutes of writes lost (depending on
# the configured save points).
#
# The Append Only File is an alternative persistence mode that provides
# much better durability. For instance using the default data fsync policy
# (see later in the config file) Redis can lose just one second of writes in a
# dramatic event like a server power outage, or a single write if something
# wrong with the Redis process itself happens, but the operating system is
# still running correctly.
#
# AOF and RDB persistence can be enabled at the same time without problems.
# If the AOF is enabled on startup Redis will load the AOF, that is the file
# with the better durability guarantees.
#
# Please check http://redis.io/topics/persistence for more information.

# Injected by env2config, replacing default: appendonly no
appendonly yes
--

# The name of the append only file (default: "appendonly.aof")
--
dcollinsⓔenv2config:~$ env REDIS_INJECT='redis.conf:./redis.conf' \
                            REDIS_APPENDONLY=yes \
                            env2config inject ./default_configs

dcollinsⓔenv2config:~$ diff default_configs/redis/3.0.1/redis.conf ./redis.conf
504c504,505
< appendonly no
---
> # Injected by env2config, replacing default: appendonly no
> appendonly yes
```

## Supported Services

- [redis](http://redis.io/)



