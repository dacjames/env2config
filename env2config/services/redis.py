import requests as r

DEFAULT_URL = \
    'https://raw.githubusercontent.com/antirez/redis/{version}/redis.conf'


def default_configs(version):
    def get_default():
        url = DEFAULT_URL.format(version=version)
        response = r.get(url)

        if response.status_code == 200:
            text = response.text
            return text

        else:
            raise ValueError(version)

    return {
        'redis.conf': get_default
    }


def inject(version):
    return {
        'redis.conf': '/etc/redis.conf'
    }


def blacklist(version):
    return [
        'REDIS_VERSION',
        'REDIS_URL',
    ]


def convert_name(config):
    parts = config.split('_')
    formatted = '-'.join(p.lower() for p in parts)
    return formatted


def convert_value(value):
    return str(value)


def match(line, config):
    content = line.replace('#', '').strip()
    line_config = content.split(' ')[0]
    matches = line_config == config
    return matches


def replace(line, config, value):
    new_line = '{0} {1}\n'.format(config, value)
    return new_line


def comment(content):
    return '# ' + content + '\n'
