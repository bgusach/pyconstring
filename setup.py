# coding: utf-8

from __future__ import unicode_literals


from setuptools import setup
import pyconstring


def read_file(path):
    try:
        with open(path) as f:
            return f.read()
    except IOError:
        return ''

setup(
    name='pyconstring',
    version=pyconstring.__version__,
    description='Tool to handle connection strings',
    long_description=read_file('README.rst'),
    url='https://github.com/ikaros45/pyconstring',
    author='Bor González-Usach',
    author_email='bgusach@gmail.com',
    license='MIT',
    packages=[b'pyconstring', b'tests'],
    keywords='connection string',
    zip_safe=True,
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Development Status :: 4 - Beta',
        'Operating System :: OS Independent',
        'Topic :: Database',
        'Topic :: Utilities',
    ],
)
