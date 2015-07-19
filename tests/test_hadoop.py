import re

from subprocess import check_call
from future.moves.subprocess import check_output


def test_hadoop_build(tmpdir):
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


def test_hadoop_build_and_inject(tmpdir):
    dest = test_hadoop_build(tmpdir)
    hadoop_confs = str(check_output([
        'env',
        'ENV_INJECT=*.xml:-',
        'HADOOP_HDFS_DFS_NAMENODE_RPC-ADDRESS=wacky-namenode',
        'HADOOP_YARN_YARN_RESOURCEMANAGER_ADDRESS=wacky-resman',
        'HADOOP_MAPRED_MAPREDUCE_JOBTRACKER_JOBHISTORY_LOCATION=wacky-mrhistory',
        'env2config',
        'inject',
        str(dest),
    ]))

    assert 'wacky-namenode' in hadoop_confs
    assert 'wacky-resman' in hadoop_confs
    assert 'wacky-mrhistory' in hadoop_confs

    assert len(list(re.finditer('Injected by env2config', hadoop_confs))) == 3
