# coding: utf-8

from setuptools import setup
from setuptools import find_packages


def read_file(path):
    try:
        with open(path) as f:
            return f.read()
    except IOError:
        return ''


setup(
    name='pyconstring',
    version='1.0.0',
    description='Tool to handle connection strings',
    long_description=read_file('README.rst'),
    url='https://github.com/bgusach/pyconstring',
    author='Bor González-Usach',
    author_email='bgusach@gmail.com',
    license='MIT',
    keywords='connection string',
    zip_safe=True,
    package_dir={'': 'src'},
    packages=find_packages('src'),
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Development Status :: 5 - Production/Stable',
        'Operating System :: OS Independent',
        'Topic :: Database',
        'Topic :: Utilities',
    ],
)
