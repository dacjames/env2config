import os
import sys
import json
from fnmatch import fnmatch

import env2config.services
import env2config.util as util
from env2config.interface import ServiceDefinition


logger = util.create_logger()


ENV_INJECT_KEY = 'ENV_INJECT'


def _service_path(root, service_name):
    return os.path.join(root, service_name)


def _version_path(root, service_name, version):
    service = _service_path(root, service_name)
    return os.path.join(service, version)


def _inject_string_to_dict(string, potential_filenames):
    logger.debug('reading injection spec "%s"', string)
    config_pairs = string.split(',')
    config_dict = {}
    for config_pair in config_pairs:
        src, dest = config_pair.split(':')

        # kinda blobbing
        for filename in potential_filenames:
            if fnmatch(filename, src):
                config_dict[filename] = dest

    logger.debug('parsed injection spec as %s', config_dict)

    return config_dict


def build(service_name, version, root_config_dir):
    '''Build Step'''

    service_class = ServiceDefinition.get_service_class(service_name)
    service = service_class(version)

    default_configs = service.default_configs()

    # Create all of the directories that we need.
    # Go one-by-one to improve error reporting.

    # e.g. ./default_configs
    if not os.path.exists(root_config_dir):
        logger.debug('creating root path: %s', root_config_dir)
        os.mkdir(root_config_dir)

    # e.g. ./default_configs/redis
    service_root = _service_path(root_config_dir, service_name)
    if not os.path.exists(service_root):
        logger.debug('creating service root path: %s', service_root)
        os.mkdir(service_root)

    # e.g. ./default_configs/redis/3.0.1
    version_root = _version_path(root_config_dir, service_name, version)
    if not os.path.exists(version_root):
        logger.debug('creating version root path %s', version_root)
        os.mkdir(version_root)

    default_paths = {}
    for name, get_content in default_configs.items():
        path = os.path.join(version_root, name)
        logger.debug('considering default config file %s', path)

        if not os.path.exists(path):
            logger.debug('downloading  default config file %s to %s', name, path)
            content = get_content()
            with open(path, 'w') as f:
                f.write(content)
        else:
            logger.debug('file exists, not downloaded')

        default_paths[name] = path

    return True


def inject(root_config_dir):
    '''Inject Step'''

    configs_to_inject = []
    logger.debug('injecting configs from directory %s')

    # e.g. ./default_configs
    for service_name in os.listdir(root_config_dir):
        # first level, folders are service names
        # e.g. ./default_configs/redis
        logger.debug('found service %s', service_name)
        service_name_directory = os.path.join(root_config_dir, service_name)
        for version in os.listdir(service_name_directory):
            logger.debug('found service %s version %s', service_name, version)
            # second level, folders as versions
            # e.g. ./default_configs/redis/3.0.1
            version_directory = os.path.join(service_name_directory, version)
            configs_to_inject.append(
                (service_name, version, version_directory)
            )

    results = []
    for service_name, version, version_directory in configs_to_inject:
        result = _inject_service(service_name, version, version_directory)
        results.append(result)

    return all(results)


def _inject_service(service_name, version, config_dir):
    logger.debug('injecting configs for service %s version %s', service_name, version)

    # Load the service class and instantiate it.
    service_class = ServiceDefinition.get_service_class(service_name)
    service = service_class(version)

    # Determine which configuration files to inject by overriding
    # defaults defined by the service with arguments supplied in the
    # {SERVICE_NAME}_INJECT environment varible.
    # e.g. REDIS_INJECT='redis.conf:./redis.conf'
    #      => {'redis.conf': './redis.conf'}

    env_prefix = service_name.upper()

    default_filenames = list(service.default_configs().keys())

    builtin = service.config_mapping()
    logger.debug('considering default injectable configs %s', builtin)

    env_inject_string = os.environ.get(ENV_INJECT_KEY)
    if env_inject_string is None:
        env_inject = {}
    else:
        env_inject = _inject_string_to_dict(env_inject_string, default_filenames)

    configs_to_inject = dict(builtin, **env_inject)
    logger.debug('resolved to inject configs %s', configs_to_inject)

    # Collect injectable configs from all environment variables
    # beginning with the service prefix.
    # e.g. REDIS_FOO=1 => {'foo': '1'}

    injectables = {}
    blacklist = service.ignore_env_names()
    for env_name, env_value in os.environ.items():
        if env_name in blacklist:
            logger.debug('env variable %s ignore because it is in the service blacklist')
            continue

        if env_name == ENV_INJECT_KEY:
            logger.debug('env variable %s ignored because it is the injection key')
            continue

        if env_name.startswith(env_prefix):
            logger.debug('found injectable env variable %s')
            start = env_name.find('_') + 1
            config_part = env_name[start:]

            config_filename, config_part = service.config_multiplex(config_part)
            config_name = service.convert_name(config_part)
            config_value = service.convert_value(env_value)

            logger.debug('found potential inject (name: %s, value: %s) into %s', config_name, config_value, config_filename)
            injectables[config_name] = (config_filename, config_value)

    processor = service.Processor(
        service=service,
        config_dir=config_dir,
        configs_to_inject=configs_to_inject,
        injectables=injectables,
    )
    processor.process()

    return True
