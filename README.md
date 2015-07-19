# env2config

`env2config` is a simple utility for generating configuration files that allows environment variables to override vendor-provided defaults.  It is primarily designed for use with containerization technologies like [Docker](https://www.docker.com/) and can be easily extended to support new configuration file formats.

## Installation

[![Build Status](https://travis-ci.org/dacjames/env2config.svg?branch=master)](https://travis-ci.org/dacjames/env2config)

```
pip install env2config
```

As of version 0.5.0, tested with Python versions: 
* 2.6
* 2.7
* 3.3
* 3.4

## Breaking Changes

- `0.5.0`: Enabled `from __future__ import unicode_strings`.
- `0.4.0`: Injection spec variable renamed from "{service}\_INJECT" to "ENV\_INJECT".

## Usage

```sh
dcollinsⓔenv2config:~$ ls default_configs
ls: default_configs: No such file or directory
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
dcollinsⓔenv2config:~$ env ENV_INJECT='redis.conf:-' \
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
dcollinsⓔenv2config:~$ env ENV_INJECT='redis.conf:./redis.conf' \
                            REDIS_APPENDONLY=yes \
                            env2config inject ./default_configs

dcollinsⓔenv2config:~$ diff default_configs/redis/3.0.1/redis.conf ./redis.conf
504c504,505
< appendonly no
---
> # Injected by env2config, replacing default: appendonly no
> appendonly yes
```

## Injection Specification

The ENV_INJECT environment variable is used to contol what files will be injected.  It takes the form: `{src}:{dest},{src}:{dest},...`, where each `{src},{dest}` pair is known as an *injection spec*.

`{src}` can be either:

- A name of a supported default configuration file, e.g. `redis.conf`.  Must the *filename*, not a path.
- An absolute path to a configuration file, e.g. `/etc/redis/redis.conf`.  The config file must have be supported by a service definition.
- An absolute path to a directory, e.g. `/etc/redis/`.  The directory should end with a trailing '/' for clarity but it does not affect the behavior.  The directory will be searched for supported config files.
- A "glob" of any of the above, e.g. `*.conf`.  Globs are expanded using Python's builtin `fnmatch` and `glob` modules, plus `~` will expand to the current user home.

**The leading `/` is used to differentiate between a local source and a supported default config.**

`{dest}` can be either:

- An absolute path to the output configuration file path, e.g. `/data/redis.conf`
- An absolute path to a directory, e.g. `/data/`.  The directory should end with a trailing '/' for clarity but it does not affect the behavior.  Matched configs will be written to this directory with their existing filename.
- The special "file" `-`, meaning stdout.  This is especially useful for testing and debugging.

Injection specs are processed in order and override previous specs.  One common use of this feature is `ENV_INJECT='*:/dev/null,redis.conf:-`, which sends all configs except redis.conf to /dev/null and prints redis.conf to stdout.


## Supported Services

- [redis](http://redis.io/)
- [kafka](https://kafka.apache.org/)
- [hadoop](https://hadoop.apache.org/) (work in progress)


