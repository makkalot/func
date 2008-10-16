import sys
try:
    import ez_setup
    ez_setup.use_setuptools()
except ImportError:
    pass

from setuptools import setup

setup(
    name='func coverage output pluin',
    version='0.1',
    author='Adrian Likins',
    author_email = 'alikins@redhat.com',
    description = 'extended coverage output',
    license = 'public domain',
    py_modules = ['funccover'],
    entry_points = {
        'nose.plugins': [
            'funccoverplug = funccover:FuncCoverage'
            ]
        }

    )
