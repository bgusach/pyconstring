pyconstring
===========

Tool to handle connection strings. Offers an easy API that parses and constructs connection strings
in the form of ``Key=Value;``, almost as easy as handling a dictionary.



Rules
-----
There is not a universal syntax for connection strings, therefore this can't work for every single possible syntax.
However, there is a set of general rules that keeps the problems at bay, and pyconstring has been implemented following
these generic rules. Those are:

- Keys are not case sensitiv
- If a key contains an equal sign, it must be doubled in the connection string (key=1 --> 'key==1')
- Surrounding white spaces around the key or value are ignored, unless the value is quoted (' value ' --> 'value')
- Quoting of value is necessary when it contains white spaces or semicolons, or it starts with any quote
- If the value needs to be quoted, it can be quoted with single or double quotes
- However, if the value needs to be quoted, and it contains the same type quotes, those have to be doubled. If it
  contains the other type of quotes, no special handling is needed. (value"45 --> 'value"45' or "value""45")
- Normally the last appearance of a key in a connection string takes precedence, but there are some exceptions like
  `Provider`, with which the first appearance will take precedence and will not be overridden.


Usage examples
--------------
Constructing a connection string from scratch::

    >>> cs = ConnectionString()
    >>> cs['user'] = 'manuel'
    >>> cs['password'] = '1234'
    >>> cs.get_string()
    u'User=manuel;Password=1234;'

Parsing an already existing string::

    >>> from pyconstring import ConnectionString
    >>> cs = ConnectionString.from_string('key1=value1;key2=value2;')
    >>> cs['key1'] = 'another value'
    >>> cs.get_string()
    u'Key1=another value;Key2=value2;'
    >>> cs['user'] = 'johnny'
    >>> cs.get_string()
    u'Key1=another value;Key2=value2;User=johnny;'

Constructing a connection string from a dictionary::

    >>> from pyconstring import ConnectionString
    >>> cs = ConnectionString.from_dict({'key1': 'value1', 'key2': 'value2'})
    >>> cs['key1']
    'value1'
    >>> cs.get_string()
    u'Key2=value2;Key1=value1;'

Constructing a connection string from an iterable::

    >>> cs = ConnectionString.from_iterable([('key1', 'value1'), ('key2', 'value2')])
    >>> cs['key1']
    'value1'
    >>> cs.get_string()
    u'Key1=value1;Key2=value2;'


