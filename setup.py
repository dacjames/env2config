from setuptools import setup

setup(
    name='env2config',
    packages=['env2config', 'env2config.services'],
    version='0.3.0',
    scripts=['bin/env2config'],
    description='Generate config files from environment variables',
    author='Daniel Collins',
    author_email='peterldowns@gmail.com',
    url='https://github/dacjames/env2config',
    install_requires=['requests'],
    keywords=[],
    classifiers=[],
)
