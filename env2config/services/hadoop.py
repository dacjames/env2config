
import requests as r
from lxml import etree
from lxml.builder import E

from env2config.interface import RewriteOriented
from env2config.conversions import dotted_lower

HADOOP_URL = "https://hadoop.apache.org/docs/r{version}/{config_path}"


class HadoopDefinition(RewriteOriented):
    service_name = 'hadoop'

    def default_configs(self):
        def loader(config_path):
            url = HADOOP_URL.format(version=self.version, config_path=config_path)
            response = r.get(url)

            if response.status_code == 200:
                text = response.text
                return text

            else:
                raise ValueError(url)

        return {
            'hdfs-site.xml': lambda: loader('hadoop-project-dist/hadoop-hdfs/hdfs-default.xml'),
            'yarn-site.xml': lambda: loader('hadoop-yarn/hadoop-yarn-common/yarn-default.xml'),
            'mapred-site.xml': lambda: loader('hadoop-mapreduce-client/hadoop-mapreduce-client-core/mapred-default.xml'),
        }

    def config_mapping(self):
        return {
            'hdfs-site.xml': '/etc/hadoop/conf/hdfs-site.xml'
        }

    def convert_name(self, config_value):
        return dotted_lower(config_value)

    def ignore_env_names(self):
        return [
            'HADOOP_VERSION',
            'HADOOP_URL',
            'HADOOP_HOME',
        ]

    def parse_file(self, text_content):
        xml = etree.XML(text_content)
        properties = xml.iter('property')
        pairs = (
            (
                prop.get('name', ''),
                (prop.get('value'), prop.get('description', ''))
            ) for prop in properties
        )

        return dict(pairs)

    def inject_file(self, default_model, config_model):
        updated_model = dict(default_model, **config_model)

        properties = []
        for name, (value, description) in updated_model:
            properties.append(E.property(
                name=name,
                value=value,
                description=description,
            ))

        xml = E.configuration(*properties)
        xml_text = etree.tostring(xml)
        return xml_text
