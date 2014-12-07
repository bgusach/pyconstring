# coding: utf-8

from __future__ import unicode_literals


from setuptools import setup
import pyconstring


setup(
    name='pyconstring',
    version=pyconstring.__version__,
    description='Tool to handle connection strings',
    url='https://github.com/ikaros45/pyconstring',
    author='Bor González-Usach',
    author_email='bgusach@gmail.com',
    license='MIT',
    packages=[b'pyconstring', b'tests'],
    keywords='connection string',
    zip_safe=True,
)
