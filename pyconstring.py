# coding: utf-8

"""

"""

from __future__ import unicode_literals

from collections import OrderedDict
from operator import methodcaller


class ParseError(Exception):
    pass


class ConnectionString(object):

    def __init__(self, string='', key_formatter=methodcaller('title'), key_translator=None,
                 prio_keys=('Provider',)):
        """
        :param unicode string: connection string

        """
        self._store = self._meta__COMPOSED_CLASS()
        self._key_formatter = key_formatter or (lambda k: k)
        self._key_translator = key_translator or (lambda k: k)
        self._priority_keys = {self._key_formatter(k) for k in prio_keys}

        self.load_string(string)

    @property
    def params(self):
        return self._store.copy()

    def load_string(self, string):
        self._store = self._meta__COMPOSED_CLASS()

        pairs = self._fetch_pairs(string)

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
        if start not in cls.QUOTES:
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

        if not (val.startswith(' ') or val.endswith(' ') or ';' in val or val[0] in cls.QUOTES):
            return val

        # Find out what kind of quotes we need to use
        quotes_in_val = cls.QUOTES.intersection(val)

        if not quotes_in_val:  # If no quotes, just use double
            return '"%s"' % val

        if len(quotes_in_val) == 1:
            return '{quote}{val}{quote}'.format(val=val, quote=cls.QUOTES.difference(quotes_in_val).pop())

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
    def fromdict(self):
        raise NotImplementedError

    @classmethod
    def fromstring(cls):
        raise NotImplementedError

    __getitem__ = lambda self, key: self._store[self._key_formatter(key)]
    __setitem__ = lambda self, key, value: self._store.__setitem__(key, value)

    @classmethod
    def _fetch_pairs(cls, string):
        """
        Parses the string and stores its parameters. Overwrites any existing state.

        :param unicode string: connection string to be loaded

        :raises: ValueError when an expected token is not found
        # TODO [ik45 27.09.2014]: consider a method to include the missing token in the exception

        """
        string = string.strip()
        if not string.endswith(';'):
            string += ';'

        while string:

            tok_end = string.index('=')

            # If next char is also '=', find next '='
            if string[tok_end+1] == '=':
                tok_end = string.index('=', tok_end+2)

            key, string = string[:tok_end].rstrip(), string[tok_end+1:].lstrip()
            # print 'key: %r -- rest %r' % (key, string)

            first = string[0]

            # If first char is quote, find the first semicolon after the next quote
            if first in cls.QUOTES:
                last_quote_pos = 0

                while True:
                    tok_end = string.index(';', string.index(first, last_quote_pos+1))

                    # If next char is not a quote, we found the end of the literal
                    if string[tok_end+1:tok_end+2] != first:
                        break

                    # Otherwise, keep searching
                    last_quote_pos = tok_end
            else:
                tok_end = string.index(';')

            value, string = string[:tok_end].rstrip(), string[tok_end+1:].lstrip()

            # print 'val: %r -- rest %r' % (value, string)
            yield key, value

    QUOTES = {'"', "'"}
    SPECIAL_CHARS = {'"', "'", ';', '='}
    SPECIAL_VALUE_STARTER = {' ', '"', "'"}

    def resolve(self):
        """
        Returns the composed string

        :rtype: unicode

        """
        if not self._store:
            return ''

        return ';'.join('%s=%s' % (self._encode_key(k), self._encode_value(v)) for k, v in self._store.iteritems()) + ';'

    def __repr__(self):
        return '<ConnectionString %s>' % self.resolve()

    _meta__COMPOSED_CLASS = OrderedDict
    _meta__EXPOSED_METHODS = [
        'keys', 'iterkeys', 'values', 'itervalues', 'viewitems', 'viewvalues',
        '__iter__', 'update', 'get', 'copy',
        # '__getitem__',
        '__setitem__', 'iteritems',
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

            composed_class = attrs['_meta__COMPOSED_CLASS']

            # Expose the declared attributes, (as longs as the exist in the container class)
            attrs.update({
                name: create_proxy(name)
                for name in filter(lambda attr: hasattr(composed_class, attr), attrs.pop('_meta__EXPOSED_METHODS'))
            })

            return type(cls_name, bases, attrs)
