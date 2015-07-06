FROM debian:jessie

RUN apt-get update && \
    apt-get install -y -q python curl && \
    curl https://bootstrap.pypa.io/get-pip.py | python && \
    pip install env2config

RUN env2config build redis 3.0.1 /default_configs

COPY bin/docker-entrypoint.sh /entrypoint.sh
ENTRYPOINT /entrypoint.sh

