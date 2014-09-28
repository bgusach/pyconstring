# coding: utf-8

"""

"""

from __future__ import unicode_literals

from collections import OrderedDict
from operator import methodcaller


class ParseError(Exception):
    pass


class ConnectionString(object):

    def __init__(self, string='', key_formatter=methodcaller('capitalize'), key_translator=lambda k: k):
        """
        :param unicode string: connection string

        """
        self._store = self._meta__COMPOSED_CLASS()
        self._key_formatter = key_formatter
        # TODO [ik45 28.09.2014]: implement translation!
        self._key_translator = key_translator

        # TODO [ik45 28.09.2014]: NON_OVERRIDABLE_KEYS have to be processed as well by key_formatter!

        self.load_string(string)

    @property
    def params(self):
        return self._store.copy()

    def load_string(self, string):
        self._store = {}

        pairs = self._process_pairs(self._fetch_pairs(string))

        for key, value in pairs:
            self._store_pair(key, value)

    NON_OVERRIDABLE_KEYS = frozenset(['Provider'])

    @classmethod
    def _process_pairs(cls, pairs):
        """
        Removes quotation and checks that key and values are correct

        :param pairs:
        :return:
        """
        for key, value in pairs:

            start_value = value[0]
            if start_value in cls.QUOTES:
                if not value.endswith(start_value):
                    raise Exception('Incorrect quotation')

                value = value.strip(start_value)

            yield key, value

    def _store_pair(self, key, value):
        """
        Stores key-value pair, applying formatting to the key

        """
        # TODO [ik45 28.09.2014]: partially wrong! we do want to override explicitly some keys
        key = self._key_formatter(key.strip())
        if key in self.NON_OVERRIDABLE_KEYS:
            return

        self._store[key] = value

    def __setitem__(self, key, value):
        key = self._key_formatter(key)
        if key.endswith('='):
            raise KeyError(key)

        raise NotImplementedError
        self._store[self._key_formatter(key)] = value

    @classmethod
    def fromdict(self):
        raise NotImplementedError

    __getitem__ = lambda self, key: self._store[self._key_formatter(key)]

    @classmethod
    def _fetch_pairs(cls, string):
        """
        Parses the string and stores its parameters. Overwrites any existing state.

        :param unicode string: connection string to be loaded

        :raises: ValueError when an expected token is not found
        # TODO [ik45 27.09.2014]: consider a method to include the missing token in the exception

        """
        string = string.strip()

        while string:

            tok_end = string.index('=')

            # If next char is also '=', find next '='
            if string[tok_end+1] == '=':
                tok_end = string.index('=', tok_end+2)

            key, string = string[:tok_end].rstrip(), string[tok_end+1:].lstrip()
            # print 'key: %r -- rest %r' % (key, string)

            first = string[0]

            # If starting with quotes, find the first semicolon after the next quote
            if first in cls.QUOTES:
                tok_end = string.index(';', string.index(first, 1))
            else:
                tok_end = string.index(';')

            value, string = string[:tok_end].rstrip(), string[tok_end+1:].lstrip()

            # print 'val: %r -- rest %r' % (value, string)
            yield key, value

    QUOTES = {'"', "'"}
    SPECIAL_CHARS = {'"', "'", ';', '='}
    SPECIAL_VALUE_STARTER = {' ', '"', "'"}

    def string(self):
        """
        Returns the composed string

        :rtype: unicode

        """
        def format(key, val):
            if '=' in key:
                key = key.replace('=', '==')
            if val.startswith(' '):
                val = '"%s"' % val

            if not self.SPECIAL_CHARS.intersection(val):
                return key, val

            quote = self.QUOTES.intersection(val)
            if not quote:
                return key, '"%s"' % val



        return ';'.join('%s=%s' % pair for pair in self._store.iteritems())

    def __repr__(self):
        return '<ConnectionString "%s">' % self.string

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
