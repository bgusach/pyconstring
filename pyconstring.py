# coding: utf-8

"""

"""

from __future__ import unicode_literals

import re
import sys

from collections import OrderedDict
from operator import methodcaller


__all__ = ['ConnectionString']



class ConnectionString(object):

    # Following attributes can be overridden to customize behaviour

    # Method that processes the key string. Accepts a string and returns a string
    _key_formatter = staticmethod(methodcaller('title'))

    # Method that translates the key string. Accepts a string and returns a string
    _key_translator = staticmethod(lambda k: k)

    # Keys that won't be overridden if they appear more than once in the connection string to be loaded
    _non_overridable_keys = ['Provider']

    # Dict-like class to store the key-value pairs
    _container_class = OrderedDict

    # Methods of the container class to be exposed on the ConnectionString interface
    _container_exposed_methods = [
        'keys', 'iterkeys', 'values', 'itervalues', 'viewitems', 'viewvalues',
        '__iter__', 'get', 'items', 'iteritems', '__len__',
    ]

    def __init__(self):
        self._store = self._container_class()
        self._formatted_prio_keys = {self._key_formatter(k) for k in self._non_overridable_keys}

    def copy_store(self):
        """
        Returns a copy of the inner store

        """
        return self._store.copy()

    def _load_string(self, string):
        """
        Parses and loads an string into `self`

        :param unicode string: connection string to be loaded

        """
        if string:
            self._load_pairs(self._fetch_pairs(string), no_overriding=True)

    def _load_pairs(self, pairs, no_overriding=False):
        """
        Loads key-val pairs into `self` not overriding the priority keys

        """
        pred = self._is_settable if no_overriding else lambda k: True

        for key, value in (self._decode_pair(k, v) for k, v in pairs if pred(k)):
            self._store_pair(key, value)

    @staticmethod
    def _decode_key(key):
        """
        Decodes the passed key

        :param unicode key: key to be decoded
        :return: decoded key
        :rtype: unicode
        :raises: ValueError

        """
        if not key:
            raise ValueError('Key cannot be empty string')

        return key.strip().replace('==', '=')

    @staticmethod
    def _encode_key(key):
        """
        Encodes the passed key

        :param unicode key:
        :return: encoded key
        :rtype: unicode
        :raises: ValueError

        """
        if not key:
            raise ValueError('Key cannot be empty string')

        return key.strip().replace('=', '==')

    @classmethod
    def _decode_value(cls, val):
        """
        Decodes the passed value

        :param unicode val: value to be decoded
        :return: decoded value
        :rtype: unicode
        :raises: ValueError

        """
        val = val.strip()

        # Empty string
        if not val:
            return val

        # If it does not start with quotes, no decoding needed
        start = val[0]
        if start not in cls._QUOTES:
            return val

        # Handle value starting with quote but not finishing with quote as well
        if not val.endswith(start) or len(val) == 1:  # just a quote is a wrong value
            raise ValueError('Incorrect quotation')

        # Remove wrapping quotes, and reduce any double inner quote
        return val[1:-1].replace(start * 2, start)

    @classmethod
    def _encode_value(cls, val):
        """
        Encodes the passed value

        :param unicode val: value to be encoded
        :return: encoded value
        :rtype: unicode
        :raises: ValueError

        """
        if not val:
            return val

        # Return if no special characters that would require quoting
        if not (
            val.startswith(' ')
            or val.endswith(' ')
            or ';' in val
            or val[0] in cls._QUOTES  # Starts with quotes
        ):
            return val

        # Get what kind of quotes are present in value
        quotes_in_val = cls._QUOTES.intersection(val)

        # If no quotes, just use double
        if not quotes_in_val:
            return '"%s"' % val

        # If only one type, use the other one to quote around
        if len(quotes_in_val) == 1:
            return '{quote}{val}{quote}'.format(val=val, quote=cls._QUOTES.difference(quotes_in_val).pop())

        # If both types of quotes in string, escape the double quotes by doubling them
        return '"%s"' % val.replace('"', '""')

    @classmethod
    def _encode_pair(cls, key, val):
        """
        Encodes a pair key-value

        """
        return cls._encode_key(key), cls._encode_value(val)

    @classmethod
    def _decode_pair(cls, key, val):
        """
        Decodes a pair key-value

        """
        return cls._decode_key(key), cls._decode_value(val)

    def _store_pair(self, key, value):
        """
        Stores key-value pair, applying formatting to the key

        """
        self._store[self._key_formatter(key)] = value

    def _is_settable(self, key):
        """
        Returns whether the key can be set or not

        :rtype: bool

        """
        return key not in self._formatted_prio_keys or key not in self._store

    @classmethod
    def from_string(cls, string):
        """
        Creates a new instance and loads the passed string

        :param unicode string: connection string to be parsed
        :rtype: ConnectionString

        """
        self = cls()
        self._load_string(string)

        return self

    @classmethod
    def from_dict(cls, params):
        """
        Creates instance and loads the passed parameters on it

        :param dict params: parameters to be loaded
        :rtype: ConnectionString

        """
        self = cls()
        self._load_pairs(params.iteritems())
        return self

    @classmethod
    def from_iterable(cls, iterable):
        """
        Creates instance and loads the passed iterable of key-values on it

        :param iterable: iterable of key-values
        :rtype: ConnectionString

        """
        self = cls()
        self._load_pairs(iterable)
        return self

    # Direct Item access needs key formatting
    __getitem__ = lambda self, key: self._store.__getitem__(self._key_formatter(key))
    __setitem__ = lambda self, key, value: self._store.__setitem__(self._key_formatter(key), value)
    __delitem__ = lambda self, key: self._store.__delitem__(self._key_formatter(key))
    __contains__ = lambda self, key: self._store.__contains__(self._key_formatter(key))

    _QUOTES = {'"', "'"}

    _RES = {
        '=': re.compile('[^=](=)[^=]'),
        '"': re.compile('(?:[""]*)"\s*(;)'),
        "'": re.compile("(?:['']*)'\s*(;)"),
        ';': re.compile('(;)'),
        'nonblank': re.compile('\S'),
    }

    @classmethod
    def _fetch_pairs(cls, string):
        """
        Parses the string and stores its parameters. Overwrites any existing state.

        :param unicode string: connection string to be loaded
        :raises: ValueError when an expected token is not found

        """
        string = string.strip()
        if string and not string.endswith(';'):
            string += ';'

        tok_start = 0
        last_start = len(string) - 1

        while tok_start < last_start:

            # Identify first non double equal sign
            match = cls._RES['='].search(string, tok_start)
            if not match:
                raise ValueError('Token not found: "="')

            tok_end = match.start(1)
            key = string[tok_start:tok_end]

            tok_start = tok_end + 1

            # Find next non blank character
            match = cls._RES['nonblank'].search(string, tok_start)
            if not match:
                raise ValueError('Only blank characters after key delimiter "="')

            tok_start = match.start(0)

            # If nonblank char is a quote, use corresponding regex to closing quote + ';'. Otherwise just look for ';'
            match = cls._RES.get(match.group(0), cls._RES[';']).search(string, tok_start)
            if not match:
                raise ValueError('Token not found ";"')

            tok_end = match.start(1)
            value = string[tok_start:tok_end]

            yield key, value

            tok_start = tok_end + 1

    def copy(self):
        """
        Returns a copy of this ConnectionString object

        """
        copy = type(self)()
        copy.update(self)

        return copy

    def update(self, other):
        """
        Updates the inner store with another ConnectionString object, other dict or iterable key-value pairs

        """
        if isinstance(other, (dict, ConnectionString)):
            self._load_pairs(other.items())
            return

        self._load_pairs(other)

    def resolve(self):
        """
        Returns the composed string

        :rtype: unicode

        """
        if not self._store:
            return ''

        return ';'.join('%s=%s' % (self._encode_key(k), self._encode_value(v))
                        for k, v in self._store.iteritems()) + ';'

    def __unicode__(self):
        return self.resolve()

    def __str__(self):
        return self.resolve() if sys.version_info > (3, 0) else self.resolve().encode('utf-8')

    def __repr__(self):
        string = self.resolve()
        return '<ConnectionString%s>' % ' ' + string if string else ''

    class __metaclass__(type):
        """
        Metaclass to expose declared attributes

        """
        def __new__(mcs, cls_name, bases, attrs):

            def create_proxy(method_name):
                """
                Creates a function that redirects the call to the underlying store object for the `method_name`

                :param bytes method_name: name of method to be exposed

                """
                def proxy(self, *args, **kwargs):
                    return getattr(self._store, method_name)(*args, **kwargs)

                proxy.__name__ = bytes(method_name)

                return proxy

            container_class = attrs['_container_class']

            # Expose the declared attributes, (as longs as the exist in the container class)
            attrs.update(
                (name, create_proxy(name))
                for name in filter(lambda attr: hasattr(container_class, attr), attrs.pop('_container_exposed_methods'))
            )

            return type(cls_name, bases, attrs)

