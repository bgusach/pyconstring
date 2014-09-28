# coding: utf-8

"""

"""

from __future__ import unicode_literals

import re
import sys

from collections import OrderedDict
from operator import methodcaller


class ConnectionStringError(Exception):
    pass


class MissingToken(ConnectionStringError):

    def __init__(self, token):
        super(MissingToken, self).__init__(token)

    def __unicode__(self):
        return 'The token "%s" could not be found' % self.args[0]


class UnexpectedEnd(ConnectionStringError):
    pass


class ConnectionString(object):

    def __init__(self,  key_formatter=methodcaller('title'), key_translator=None, prio_keys=('Provider',)):
        """
        :param function key_formatter: callback to format keys. Input and output must be
                                       unicode strings. Use None for identity.
        :param function key_translator:
        :param iterable prio_keys: sequence of keys that must not be overridden once set.

        """
        self._store = self._meta__CONTAINER_CLASS()
        self._key_formatter = key_formatter or (lambda k: k)
        self._key_translator = key_translator or (lambda k: k)
        self._priority_keys = {self._key_formatter(k) for k in prio_keys}

    @property
    def params(self):
        return self._store.copy()

    def _load_string(self, string):
        self._load_pairs(self._fetch_pairs(string))

    def _load_pairs(self, pairs):

        for key, value in (self._decode_pair(k, v) for k, v in pairs if self._is_settable(k)):
            self._store_pair(key, value)

    @staticmethod
    def _decode_key(key):
        if not key:
            raise ValueError('Key cannot be empty string')

        return key.strip().replace('==', '=')

    @staticmethod
    def _encode_key(key):
        if not key:
            raise ValueError('Key cannot be empty string')

        return key.strip().replace('=', '==')

    @classmethod
    def _decode_value(cls, val):
        val = val.strip()

        # Empty string
        if not val:
            return val

        start = val[0]
        if start not in cls._QUOTES:
            return val

        if not val.endswith(start) or len(val) == 1:  # just a quote is a wrong value
            # TODO [ik45 28.09.2014]: concrete exception
            raise ValueError('Incorrect quotation')

        return val[1:-1].replace(start * 2, start)

    @classmethod
    def _encode_pair(cls, key, val):
        return cls._encode_key(key), cls._encode_value(val)

    @classmethod
    def _decode_pair(cls, key, val):
        return cls._decode_key(key), cls._decode_value(val)

    @classmethod
    def _encode_value(cls, val):
        if not val:
            return val

        # Check if any special character that would require quoting
        if not (val.startswith(' ') or val.endswith(' ') or ';' in val or val[0] in cls._QUOTES):
            return val

        # Find out what kind of quotes we need to use
        quotes_in_val = cls._QUOTES.intersection(val)

        if not quotes_in_val:  # If no quotes, just use double
            return '"%s"' % val

        if len(quotes_in_val) == 1:
            return '{quote}{val}{quote}'.format(val=val, quote=cls._QUOTES.difference(quotes_in_val).pop())

        # If both types of quotes in string, escape the double quotes by doubling them
        return '"%s"' % val.replace('"', '""')

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
        return key not in self._priority_keys or key not in self._store

    @classmethod
    def from_dict(cls, params, *args, **kwargs):
        """
        Creates instance and loads the passed parameters on it

        :param dict params: parameters to be loaded

        """
        self = cls(*args, **kwargs)
        self._load_pairs(params.iteritems())
        return self

    @classmethod
    def from_string(cls, string, *args, **kwargs):
        """
        Creates a new instance and loads the passed string

        :param unicode string: connection string to be parsed

        """
        self = cls(*args, **kwargs)
        self._load_string(string)
        return self

    __getitem__ = lambda self, key: self._store[self._key_formatter(key)]
    __setitem__ = lambda self, key, value: self._store.__setitem__(self._key_formatter(key), value)

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
        # TODO [ik45 27.09.2014]: consider a method to include the missing token in the exception

        """
        string = string.strip()
        if string and not string.endswith(';'):
            string += ';'

        tok_start = 0
        last_start = len(string) - 1

        while tok_start < last_start:
            # print 'tok-start:', tok_start, 'strlen', last_start

            # Identify first non double equal sign
            match = cls._RES['='].search(string, tok_start)
            if not match:
                raise MissingToken('=')

            tok_end = match.start(1)
            key = string[tok_start:tok_end]

            tok_start = tok_end + 1

            # Find next non blank character
            match = cls._RES['nonblank'].search(string, tok_start)
            if not match:
                raise UnexpectedEnd

            tok_start = match.start(0)

            # print 'rest:', string[tok_start:]
            # print 'first non empty', repr(match.group(0))
            # print 'used regex:  ', cls._res.get(match.group(0), cls._res[';']).pattern

            # If nonblank char is a quote, use corresponding regex to closing quote + ';'. Otherwise just look for ';'
            match = cls._RES.get(match.group(0), cls._RES[';']).search(string, tok_start)
            if not match:
                raise MissingToken(';')

            tok_end = match.start(1)
            value = string[tok_start:tok_end]

            # print 'result', key, value
            yield key, value

            tok_start = tok_end + 1

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

    _meta__CONTAINER_CLASS = OrderedDict
    _meta__EXPOSED_METHODS = [
        'keys', 'iterkeys', 'values', 'itervalues', 'viewitems', 'viewvalues',
        '__iter__', 'update', 'get', 'copy',
        'iteritems',
    ]

    class __metaclass__(type):
        """
        Metaclass to expose declared attributes
        """

        def __new__(mcs, cls_name, bases, attrs):

            def create_proxy(method_name):

                def proxy(self, *args, **kwargs):
                    return getattr(self._store, method_name)(*args, **kwargs)

                proxy.__name__ = str(method_name)

                return proxy

            composed_class = attrs['_meta__CONTAINER_CLASS']

            # Expose the declared attributes, (as longs as the exist in the container class)
            attrs.update({
                name: create_proxy(name)
                for name in filter(lambda attr: hasattr(composed_class, attr), attrs.pop('_meta__EXPOSED_METHODS'))
            })

            return type(cls_name, bases, attrs)
