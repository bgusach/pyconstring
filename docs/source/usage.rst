Usage
=====

Object construction
-------------------

Constructing a connection string from scratch. As you can see, the case of
the keys is converted automatically::

    >>> from pyconstring import ConnectionString
    >>> cs = ConnectionString()
    >>> cs['user'] = 'manuel'
    >>> cs['password'] = '1234'
    >>> print cs.get_string()
    User=manuel;Password=1234;

.. note::

    You can specify your own key formatter by subclassing the ConnectionString class, and overriding the ``_format_key``
    method.

Parsing an already existing string::

    >>> cs = ConnectionString.from_string('key1=value1;key2=value2;')
    >>> cs['key1'] = 'another value'
    >>> cs.get_string()
    u'Key1=another value;Key2=value2;'
    >>> cs['user'] = 'johnny'
    >>> print cs.get_string()
    Key1=another value;Key2=value2;User=johnny;

.. note::

    By default when parsing a string, if the key ``Provider`` appears more than once, the first entry will be preserved.
    You can control which keys are not overridable by subclassing and overwriting ``_non_overridable_keys``

It can be instanciated from iterable::

    >>> cs = ConnectionString([('key1', 'value1'), ('key2', 'value2')])
    >>> cs['key1']
    'value1'
    >>> print cs.get_string()
    Key1=value1;Key2=value2;

Or directly from another dictionary::

    >>> ConnectionString({'key1': 'val1', 'key2': 'val2'})
    <ConnectionString 'Key2=val2;Key1=val1;'>


Object manipulation
-------------------
The ConnectionString is a subclass of OrderedDict and therefore offers the dict API. Some examples of this::

    >>> cs = ConnectionString.from_string('key1=value1;key2=value2;')
    >>> for key, value in cs.iter():
    ...   print key, value
    ...
    Key1 value1
    Key2 value2
    >>> 'key1' in cs
    True
    >>> del cs['key1']
    >>> 'key1' in cs
    False
    >>> list(cs)
    [u'Key2']
    >>> cs['key3'] = 'hey'
    >>> cs2 = ConnectionString.from_string('hello=world;')
    >>> cs == cs2
    False
    >>> cs == cs
    True

Check the :ref:`API<api>` for more details.


Key translations made easy. For instance, useful to convert from ADODB parameters to ODBC ones::

    >>> cs['Provider'] = 'some provider'
    >>> cs['user id'] = 'chanquete'
    >>> cs.translate({'provider': 'driver', 'user id': 'uid'})
    >>> print cs.get_string()
    Driver=some provider;Uid=chanquete;
