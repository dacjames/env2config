class ServiceDefinition(object):

    def __init__(self, version):
        self.version = version

    def default_configs(self):
        pass

    def config_mapping(self):
        pass

    def ignore_env_names(self):
        pass

    def convert_name(self, config_name):
        pass

    def convert_value(self, config_value):
        pass


class LineOriented(ServiceDefinition):
    def match_line(self, line, config_name):
        pass

    def inject_line(self, old_line, config_name, config_value):
        pass

    def comment_line(self, content):
        pass


class RewriteOriented(ServiceDefinition):
    def parse_file(self, text_content):
        pass

    def inject_file(self, config_model):
        pass
