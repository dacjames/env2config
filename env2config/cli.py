import sys

USAGE = '''
USAGE:
    env2config build <service_name> <version> [<default_config_folder>=./default_configs]
    env2config inject [<default_config_folder>=./default_configs]
'''.strip()

if len(sys.argv) < 3:
    print(USAGE)
    sys.exit(1)

if sys.argv[1] not in ['build', 'inject']:
    print(USAGE)
    sys.exit(1)


if sys.argv[1] == 'build' and len(sys.argv) == 4:
    process, command, service_name, version = sys.argv
    from main import build
    build(service_name, version, './default_configs')

if sys.argv[1] == 'build' and len(sys.argv) == 5:
    process, command, service_name, version, default_config_folder = sys.argv
    from main import build
    build(service_name, version, default_config_folder)


if sys.argv[1] == 'inject' and len(sys.argv) == 2:
    process, command, default_config_folder = sys.argv
    from main import inject
    inject('./default_configs')

if sys.argv[1] == 'inject' and len(sys.argv) == 3:
    process, command, default_config_folder = sys.argv
    from main import inject
    inject(default_config_folder)
