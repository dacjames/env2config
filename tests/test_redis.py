from subprocess import check_call
from future.moves.subprocess import check_output


def test_redis_build(tmpdir):
    dest = tmpdir.mkdir('default_configs')
    
    check_call([
        'env2config',
        'build',
        'redis',
        '3.0.1',
        str(dest),
    ])

    subpaths = list(dest.visit())
    assert dest / 'redis' / '3.0.1' / 'redis.conf' in subpaths

    return dest


def test_redis_build_and_inject(tmpdir):
    dest = test_redis_build(tmpdir)

    redis_conf = str(check_output([
        'env',
        'ENV_INJECT=redis.conf:-',
        'REDIS_APPENDONLY=yes',
        'REDIS_ASDF=asdf',
        'env2config',
        'inject',
        str(dest),
    ]))

    assert 'replacing default' in redis_conf
    assert 'appendonly yes' in redis_conf
    assert 'not matching any default' in redis_conf
    assert 'asdf asdf' in redis_conf
