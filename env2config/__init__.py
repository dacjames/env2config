import os
import sys
import json

import env2config.services as services

__version__ = '0.2.0'


def _service_path(root, service_name):
    return os.path.join(root, service_name)


def _version_path(root, service_name, version):
    service = _service_path(root, service_name)
    return os.path.join(service, version)


def _inject_string_to_dict(string):
    config_pairs = string.split(',')
    config_dict = {}
    for config_pair in config_pairs:
        src, dest = config_pair.split(':')
        config_dict[src] = dest

    return config_dict


def build(service_name, version, root_config_dir):
    '''Build Step'''

    service_module = getattr(services, service_name)
    service_class = getattr(service_module, service_name)
    service = service_class(version)

    default_configs = service.default_configs()

    # Create all of the directories that we need.
    # Go one-by-one to improve error reporting.

    # e.g. ./default_configs
    if not os.path.exists(root_config_dir):
        os.mkdir(root_config_dir)

    # e.g. ./default_configs/redis
    service_root = _service_path(root_config_dir, service_name)
    if not os.path.exists(service_root):
        os.mkdir(service_root)

    # e.g. ./default_configs/redis/3.0.1
    version_root = _version_path(root_config_dir, service_name, version)
    if not os.path.exists(version_root):
        os.mkdir(version_root)

    default_paths = {}
    for name, get_content in default_configs.items():
        path = os.path.join(version_root, name)

        if not os.path.exists(path):
            content = get_content()
            with open(path, 'w') as f:
                f.write(content)

        default_paths[name] = path


def inject(root_config_dir):
    '''Inject Step'''
    configs_to_inject = []

    # e.g. ./default_configs
    for service_name in os.listdir(root_config_dir):
        # first level, folders are service names
        # e.g. ./default_configs/redis
        service_name_directory = os.path.join(root_config_dir, service_name)
        for version in os.listdir(service_name_directory):
            # second level, folders as versions
            # e.g. ./default_configs/redis/3.0.1
            version_directory = os.path.join(service_name_directory, version)
            configs_to_inject.append(
                (service_name, version, version_directory)
            )

    for service_name, version, version_directory in configs_to_inject:
        _inject_service(service_name, version, version_directory)


def _inject_service(service_name, version, config_dir):
    print('config_dir', config_dir)

    # Load the service module and extract it's interface.
    # We acces the functions we need up front to improve error handling.
    # Should this be replaced with classes?

    service_module = getattr(services, service_name)
    service_class = getattr(service_module, service_name)
    service = service_class(version)

    # Determine which configuration files to inject by overriding
    # defaults defined by the service with arguments supplied in the
    # {SERVICE_NAME}_INJECT environment varible.
    # e.g. REDIS_INJECT='redis.conf:./redis.conf'
    #      => {'redis.conf': './redis.conf'}

    env_prefix = service_name.upper()
    env_mapping_key = env_prefix + '_INJECT'

    env_inject_string = os.environ.get(env_mapping_key)
    if env_inject_string is None:
        env_inject = {}
    else:
        env_inject = _inject_string_to_dict(env_inject_string)

    builtin = service.config_mapping()
    configs_to_inject = dict(builtin, **env_inject)

    # Collect injectable configs from all environment variables
    # beginning with the service prefix.
    # e.g. REDIS_FOO=1 => {'foo': '1'}

    injectables = {}
    blacklist = service.ignore_env_names()
    for env_name, env_value in os.environ.items():
        if env_name in blacklist:
            continue

        if env_name == env_mapping_key:
            continue

        if env_name.startswith(env_prefix):
            start = env_name.find('_') + 1
            config_part = env_name[start:]

            config_name = service.convert_name(config_part)
            config_value = service.convert_value(env_value)

            injectables[config_name] = config_value

    # Scan over all configuration files and inject all injectables.
    # Has O(N*M) complexity, where N is len(default_configs)
    # and M is len(injectables).  Can we do better?

    for src, dest in configs_to_inject.items():
        default = os.path.join(config_dir, src)
        with open(default) as f:
            default_lines = f.readlines()

        output_lines = []
        matched = set()
        for default_line in default_lines:
            for name, value in injectables.items():
                if service.match_line(default_line, name):
                    new_line = service.inject_line(default_line, name, value)
                    matched.add(name)
                    note = service.comment_line('Injected by env2config, replacing default: ' + default_line.strip())
                    output_lines.append(note)
                    output_lines.append(new_line)
                    break
            else:
                output_lines.append(default_line)

        for name, value in injectables.items():
            if name not in matched:
                warning = service.comment_line('Injected by env2config, not matching any default.')
                output_lines.append(warning)
                line = service.inject_line(None, name, value)
                output_lines.append(line)

        # Write out the new, overridden configs.  If the destination is '-',
        # write the configs to stdout instead (useful for debugging).
        # Is there a way to avoid this code deduplication?

        if dest == '-':
            f = sys.stdout
            for line in output_lines:
                f.write(line)
        else:
            with open(dest, 'w') as f:
                for line in output_lines:
                    f.write(line)
