.. image:: https://img.shields.io/travis/bgusach/pyconstring/master.svg
    :alt: Travis-CI badge
    :target: https://travis-ci.org/bgusach/pyconstring


.. image:: https://readthedocs.org/projects/pyconstring/badge/?version=latest
   :alt: Read the Docs
   :target: http://pyconstring.readthedocs.io/en/latest/?badge=latest


.. image:: https://img.shields.io/pypi/v/pyconstring.svg
   :alt: PyPI Version
   :target: https://pypi.python.org/pypi/pyconstring/

pyconstring
===========

Tool to handle connection strings. Offers an easy API that parses and constructs connection strings
in the form of ``Key=Value;``, as easy as handling a dictionary. Works with both Python 2.7 and 3.x

License
-------
MIT. See `License File <https://github.com/ikaros45/pyconstring/blob/master/LICENSE>`__.


Install
-------
``pyconstring`` is on PyPI ::

    pip install pyconstring

or ::

    easy_install pyconstring

Usage examples
--------------
Constructing a connection string from scratch:

.. code:: python

    >>> from pyconstring import ConnectionString
    >>> cs = ConnectionString()
    >>> cs['user'] = 'manuel'
    >>> cs['password'] = '1234'
    >>> print cs.get_string()
    User=manuel;Password=1234;

Parsing an already existing string:

.. code:: python

    >>> cs = ConnectionString.from_string('key1=value1;key2=value2;')
    >>> cs['key1'] = 'another value'
    >>> cs.get_string()
    u'Key1=another value;Key2=value2;'
    >>> cs['user'] = 'johnny'
    >>> print cs.get_string()
    Key1=another value;Key2=value2;User=johnny;

Automated escaping when necessary:

.. code:: python

    >>> cs = ConnectionString()
    >>> cs['weird=key'] = '" weird;value  '
    >>> print cs.get_string()
    Weird==Key='" weird;value  ';

Key translation:

.. code:: python

    >>> cs['key'] = 'value'
    >>> cs.translate({'key': 'clave'})
    >>> print cs.get_string()
    Clave=value;

More information in the `documentation <http://pyconstring.readthedocs.io/en/latest/?badge=latest>`__.

If you find any bug or have any suggestion, feel free to send me an email or open an issue on github.
