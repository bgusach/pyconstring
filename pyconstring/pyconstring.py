# coding: utf-8

from __future__ import unicode_literals

import sys

from collections import OrderedDict
from operator import methodcaller


__all__ = ['ConnectionString']
__version__ = '0.4.0'


class ConnectionString(object):

    def __init__(self):
        self._store = self._store_factory()
        self._formatted_prio_keys = {self._format_key(k) for k in self._non_overridable_keys}

    # Keys that won't be overridden if they appear more than once in the connection string to be loaded
    _non_overridable_keys = ['Provider']
    _store_factory = OrderedDict
    _format_key = staticmethod(methodcaller('title'))

    @classmethod
    def from_string(cls, string):
        """
        Creates a new instance and loads the passed string

        :param unicode string: connection string to be parsed
        :rtype: ConnectionString

        """
        self = cls()
        self._store_items(self._parse_string(string.lstrip()), allow_prio_overriding=False)

        return self

    @classmethod
    def from_dict(cls, params):
        """
        Creates instance and loads the passed parameters on it

        :param dict params: parameters to be loaded
        :rtype: ConnectionString

        """
        self = cls()
        self._store_items(params.items())
        return self

    @classmethod
    def from_iterable(cls, iterable):
        """
        Creates instance and loads the passed iterable of key-values on it

        :param iterable: iterable of key-values
        :rtype: ConnectionString

        """
        self = cls()
        self._store_items(iterable)
        return self

    def _store_items(self, items, allow_prio_overriding=True):
        """
        Stores key-val items

        :param bool allow_prio_overriding: flag to allow overriding of priority keys

        """
        pred = (lambda k: True) if allow_prio_overriding else self._no_prio_conflict

        for key, value in ((k, v) for k, v in items if pred(k)):
            self._store_item(key, value)

    def _store_item(self, key, value):
        """
        Stores key-value pair, applying formatting to the key

        """
        self._store[self._format_key(key)] = value

    def _no_prio_conflict(self, key):
        """
        Returns whether the key can be set or not taking into account that priority keys cannot be overridden

        :rtype: bool

        """
        return key not in self._formatted_prio_keys or key not in self._store

    @classmethod
    def _parse_string(cls, string):
        """
        Parses the string and returns an iterable of tuples (key, value)

        :raises: ValueError

        """
        if string:
            key, string = cls._get_key_from_string(string)
            value, string = cls._get_value_from_string(string)
            yield key, value

            for pair in cls._parse_string(string):
                yield pair

    @classmethod
    def _get_key_from_string(cls, string):
        """
        Receives a leftstripped string, identifies the heading key, and returns a tuple (key, rest of the string)

        :param unicode string: substring of connection string
        :returns: rest of string left stripped and without any leading '='
        :rtype: unicode

        """
        start = 0
        while True:
            pos = string.find('=', start)
            if pos == -1:
                raise ValueError('Token delimiter not found: "="')

            if string[pos+1:pos+2] == '=':
                start = pos + 2
                continue

            key, rest = string[:pos], string[pos+1:]
            return cls._decode_key(key), rest.lstrip()

    _quotes = {'"', "'"}

    @classmethod
    def _get_value_from_string(cls, string):
        """
        Receives a left stripped string, identifies the heading value, decodes it,
        and returns a tuple (key, rest of the string)

        :param unicode string: substring of connection string
        :returns: rest of string left stripped and without any leading ';'
        :rtype: unicode
        :raises: ValueError

        """
        # Not starting with quotes
        first = string[0]
        if first not in cls._quotes:
            value, _, string = string.partition(';')
            return value.rstrip(), string

        start = 1
        while True:
            pos = string.find(first, start)
            if pos == -1:
                raise ValueError('Token delimiter not found: "%s"' % first)

            # If it is a double quote, skip and keep searching
            if string[pos] == string[pos+1]:
                start = pos + 2
                continue

            value, rest = string[:pos+1], string[pos+1:]
            return cls._decode_value(value.rstrip()), rest.lstrip(' ;')

    @staticmethod
    def _decode_key(key):
        """
        :rtype key: unicode
        :rtype: unicode
        :raises: ValueError

        """
        if not key:
            raise ValueError('Key cannot be empty string')

        return key.strip().replace('==', '=')

    @staticmethod
    def _encode_key(key):
        """
        :rtype key: unicode
        :rtype: unicode
        :raises: ValueError

        """
        if not key:
            raise ValueError('Key cannot be empty string')

        return key.strip().replace('=', '==')

    @classmethod
    def _decode_value(cls, val):
        """
        :rtype val: unicode
        :rtype: unicode
        :raises: ValueError

        """
        val = val.strip()

        if not val:
            return val

        # If it does not start with quotes, no decoding needed
        start = val[0]
        if start not in cls._quotes:
            return val

        # Remove wrapping quotes, and reduce any double inner quote
        return val[1:-1].replace(start * 2, start)

    @classmethod
    def _encode_value(cls, val):
        """
        :rtype val: unicode
        :rtype: unicode
        :raises: ValueError

        """
        if not val:
            return val

        # No special characters that would require quoting
        if not (
            val.startswith(' ')
            or val.endswith(' ')
            or ';' in val
            or val[0] in cls._quotes
        ):
            return val

        # Get what kind of quotes are present in value
        quotes_in_val = cls._quotes.intersection(val)

        if not quotes_in_val:
            return '"%s"' % val

        if len(quotes_in_val) == 1:
            return '{quote}{val}{quote}'.format(val=val, quote=cls._quotes.difference(quotes_in_val).pop())

        # If both types of quotes in string, escape the double quotes by doubling them
        return '"%s"' % val.replace('"', '""')

    def copy(self):
        """
        Returns a copy of the current ConnectionString

        :rtype: ConnectionString

        """
        copy = type(self)()
        copy.update(self)

        return copy

    def copy_store(self):
        """
        Returns a copy of the inner store

        :rtype: OrderedDict
        """
        return self._store.copy()

    def update(self, other):
        """
        Updates the state of self with another ConnectionString object, other dict or iterable key-value pairs

        :type other: ConnectionString|dict|iterable of tuples

        """
        if isinstance(other, (dict, ConnectionString)):
            self._store_items(other.items())
            return

        self._store_items(other)

    def translate(self, trans, strict=True):
        """
        Translates the keys of the store.

        :param dict trans: translation mapping {pre name: post name}
        :param bool strict: When strict, the existing keys in self that
                            are not in `trans` will be removed. If not strict,
                            they will still exist.

        """
        trans = {self._format_key(key): value for key, value in trans.items()}
        pred = trans.__contains__ if strict else lambda x: True

        translated_items = [(trans.get(key, key), value) for key, value in self.items() if pred(key)]

        self.clear()
        self._store_items(translated_items)

    def get_string(self):
        """
        :returns: the composed connection string
        :rtype: unicode

        """
        if not self._store:
            return ''

        return ';'.join('%s=%s' % (self._encode_key(k), self._encode_value(v))
                        for k, v in self._store.items()) + ';'

    def __unicode__(self):
        return self.get_string()

    def __str__(self):
        return self.get_string() if sys.version_info > (3, 0) else self.get_string().encode('utf-8')

    def __repr__(self):
        string = self.get_string()
        return '<ConnectionString%s>' % ' ' + string if string else ''

    def __getattr__(self, item):
        """
        Redirect non defined attributes to underlying store

        """
        try:
            return getattr(self._store, item)
        except AttributeError:
            raise AttributeError("'%s' object has no attribute '%s'" % (type(self).__name__, item))

    def __eq__(self, other):
        return self._store == other.copy_store()

    def __ne__(self, other):
        return not self == other

    # Magic methods to be redirected to underlying store
    __setitem__ = _store_item
    __getitem__ = lambda self, key: self._store.__getitem__(self._format_key(key))
    __delitem__ = lambda self, key: self._store.__delitem__(self._format_key(key))
    __contains__ = lambda self, key: self._store.__contains__(self._format_key(key))
    __len__ = lambda self: len(self._store)
    __iter__ = lambda self: iter(self._store)

