from subprocess import check_call
from future.moves.subprocess import check_output


def test_kafka_build(tmpdir):
    dest = tmpdir.mkdir('default_configs')
    check_call([
        'env2config',
        'build',
        'kafka',
        '0.8.2.0',
        str(dest),
    ])

    subpaths = list(dest.visit())

    assert dest / 'kafka' / '0.8.2.0' / 'log4j.properties' in subpaths
    assert dest / 'kafka' / '0.8.2.0' / 'zookeeper.properties' in subpaths
    assert dest / 'kafka' / '0.8.2.0' / 'server.properties' in subpaths

    return dest


def test_kafka_build_and_inject(tmpdir):
    dest = test_kafka_build(tmpdir)

    kafka_conf = str(check_output([
        'env',
        'ENV_INJECT=*.properties:/dev/null,server.properties:-',
        'KAFKA_SERVER_ZOOKEEPER_CONNECT=zookeeper:2181/foo/bar',
        'KAFKA_SERVER_ASDF=asdf',
        'env2config',
        'inject',
        str(dest),
    ]))

    assert 'replacing default' in kafka_conf
    assert 'zookeeper.connect=zookeeper:2181/foo/bar' in kafka_conf
    assert 'not matching any default' in kafka_conf
    assert 'asdf=asdf' in kafka_conf
