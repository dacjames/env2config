import sys

from env2config.main import build
from env2config.main import inject

USAGE = '''
USAGE:
    env2config build <service_name> <version> [<default_config_folder>=./default_configs]
    env2config inject [<default_config_folder>=./default_configs]
'''.strip()

def ensure(result):
    if result is True:
        sys.exit(0)
    else:
        sys.exit(2)

if len(sys.argv) < 2:
    print(USAGE)
    sys.exit(1)

if sys.argv[1] not in ['build', 'inject']:
    print(USAGE)
    sys.exit(1)

if sys.argv[1] == 'build' and len(sys.argv) == 4:
    process, command, service_name, version = sys.argv
    ensure(build(service_name, version, './default_configs'))

if sys.argv[1] == 'build' and len(sys.argv) == 5:
    process, command, service_name, version, default_config_folder = sys.argv
    ensure(build(service_name, version, default_config_folder))

if sys.argv[1] == 'inject' and len(sys.argv) == 2:
    process, command, default_config_folder = sys.argv
    ensure(inject('./default_configs'))

if sys.argv[1] == 'inject' and len(sys.argv) == 3:
    process, command, default_config_folder = sys.argv
    ensure(inject(default_config_folder))

print(USAGE)
sys.exit(1)
