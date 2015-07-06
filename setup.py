from setuptools import setup

from env2config import __version__

setup(
    name='env2config',
    version=__version__,
    py_modules=['env2config'],
    scripts=['bin/env2config'],
)
