# coding: utf-8

"""
Unittests for pyconstring
"""

from __future__ import unicode_literals

import unittest
import itertools

from pyconstring import ConnectionString


class TestConnectionString(unittest.TestCase):

    def test_1(self):
        """
        Simple connection strings without special characters (= or ;) in values

        """
        cs = 'Provider=someone;User=bartolo;'
        expected = {
            'Provider': 'someone',
            'User': 'bartolo',
        }
        obj = ConnectionString(cs)

        for key, val in expected.iteritems():
            self.assertEqual(obj[key], val)

    def test_2(self):
        """
        'Priority' keys are not overridden

        """
        prio_key = 'some key'

        pairs = [
            (prio_key, 'initial'),
            (prio_key, 'second'),
        ]

        expected = {
            prio_key: 'initial',
        }
        obj = ConnectionString(';'.join('%s=%s' % p for p in pairs) + ';', prio_keys=[prio_key], key_formatter=None)

        for key, val in expected.iteritems():
            self.assertEqual(obj[key], val)

    def test_3(self):
        """
        Spaces and special characters are respected in values if they are properly quoted

        """
        template = '==hu%sehue  ;=='
        for q1, q2 in itertools.product('"', "'"):
            val = template % q2  # Insert a quote of the other type to make it more messy
            cs = 'Key1={q1}{val}{q1};'.format(q1=q1, val=val)
            obj = ConnectionString(cs)
            self.assertEqual(obj['Key1'], val)

    def test_4(self):
        """
        Spaces are properly stripped

        """
        obj = ConnectionString('    Key   =   value   ;')
        self.assertEqual(obj['Key'], 'value')

    def test_5(self):
        """
        Double equal signs are converted to one in the key

        """
        obj = ConnectionString('Key==2=value;')
        self.assertEqual(obj['Key=2'], 'value')

    def test_6(self):
        """
        Keys are properly formatted

        """
        obj = ConnectionString('cool key  =value;')

        self.assertTrue('cool key' not in obj)
        self.assertTrue('Cool Key' in obj)

        # Now with another key formatter
        obj = ConnectionString('key=value;', key_formatter=lambda x: x.upper())
        self.assertTrue('key' not in obj)
        self.assertTrue('KEY' in obj)

    def test_7(self):
        """
        Keys are formatted before look up

        """
        obj = ConnectionString('key=value;')

        self.assertEqual(obj['kEY'], 'value')

    # def test_8(self):
    #     """
    #     If the value starts with '=', it will be quoted
    #
    #     """
    #     obj = ConnectionString('key==value;')
    #     assert

    def test_9(self):
        """
        Connection strings without trailing ';' are also processed

        """
        obj = ConnectionString('huehue=troll')
        self.assertEqual(obj['huehue'], 'troll')

    def test_10(self):
        """
        Double quotes in literals are converted to one (escaping system)

        """
        obj = ConnectionString('huehue="troll\'s friend name is ""johnny""";')
        self.assertEqual(obj['huehue'], 'troll\'s friend name is "johnny"')
