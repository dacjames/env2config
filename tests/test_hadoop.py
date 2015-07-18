from subprocess import check_call
from future.moves.subprocess import check_output


def test_kafka_build(tmpdir):
    dest = tmpdir.mkdir('default_configs')
    check_call([
        'env2config',
        'build',
        'hadoop',
        '2.7.0',
        str(dest),
    ])

    subpaths = list(dest.visit())

    assert dest / 'hadoop' / '2.7.0' / 'hdfs-site.xml' in subpaths

    return dest

