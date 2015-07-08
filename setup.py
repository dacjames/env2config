from setuptools import setup

from env2config import __version__

setup(
    name='env2config',
    packages=['env2config'],
    version=__version__,
    scripts=['bin/env2config'],
    description='Generate config files from environment variables',
    author='Daniel Collins',
    author_email='peterldowns@gmail.com',
    url='https://github/dacjames/env2config',
    keywords=[],
    classifiers=[],
)
