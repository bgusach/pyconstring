# coding: utf-8

"""

"""

from __future__ import unicode_literals

try:
    from itertools import izip as zip
except ImportError:
    pass

from itertools import (
    takewhile,
    dropwhile,
)

import itertools as it


class ConnectionString(object):

    def __init__(self, string=''):
        """
        :param unicode string: connection string

        """
        self._store = self._meta__COMPOSED_CLASS()
        self.load_string(string)

    @property
    def params(self):
        return self._store.copy()

    def load_string(self, string):
        d = {}
        for key, value in self._process_pairs(self._fetch_pairs(string)):
            if key in self.NON_OVERRIDABLE_KEYS and key in d:
                continue

            d[key] = value

    NON_OVERRIDABLE_KEYS = {'Provider'}

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

    @classmethod
    def _fetch_pairs(cls, string):
        """
        Parses the string and stores its parameters. Overwrites any existing state.

        :param unicode string: connection string to be loaded

        """
        string = string.lstrip()

        while string:
            rest = iter(string)
            key = ''.join(takewhile('='.__ne__, rest)).rstrip()
            rest = dropwhile(' '.__eq__, rest)

            value = ''.join(takewhile(';'.__ne__, rest)).rstrip()

            yield key, value
            string = ''.join(rest).lstrip()

    QUOTES = ('"', "'")
    SPECIAL_CHARS = {'"', "'", ';', '='}

    def get_string(self):
        """
        Returns the composed string

        :rtype: unicode

        """
        return ';'.join('%s=%s' % pair for pair in self._store.iteritems())

    def __repr__(self):
        return '<ConnectionString "%s">' % self.get_string()

    _meta__COMPOSED_CLASS = dict
    _meta__EXPOSED_METHODS = [
        'keys', 'iterkeys', 'values', 'itervalues', 'viewitems', 'viewvalues',
        '__iter__', 'update', 'get', 'copy', '__getitem__', '__setitem__', 'iteritems',
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
                for name in filter(vars(composed_class).__contains__, attrs.pop('_meta__EXPOSED_METHODS'))
            })

            return type(cls_name, bases, attrs)
