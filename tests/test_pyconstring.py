# coding: utf-8

"""
Unittests for pyconstring
"""

from __future__ import unicode_literals

import unittest

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
        obj = ConnectionString.from_string(cs)

        for key, val in expected.items():
            self.assertEqual(obj[key], val)

    def test_2(self):
        """
        'Priority' keys are not overridden

        """
        prio_key = ConnectionString._non_overridable_keys[0]

        pairs = [
            (prio_key, 'initial'),
            (prio_key, 'second'),
        ]

        expected = {
            prio_key: 'initial',
        }
        obj = ConnectionString.from_string(';'.join('%s=%s' % p for p in pairs))

        for key, val in expected.items():
            self.assertEqual(obj[key], val)

    def test_3(self):
        """
        Spaces and special characters are respected in values if they are properly quoted

        """
        template = '==hu%sehue  ;=='
        for q1, q2 in [('"', "'"), ("'", '"')]:
            val = template % q2  # Insert a quote of the other type to make it more messy
            cs = 'Key1={q1}{val}{q1};'.format(q1=q1, val=val)
            obj = ConnectionString.from_string(cs)
            self.assertEqual(obj['Key1'], val)

    def test_4(self):
        """
        Spaces are properly stripped

        """
        obj = ConnectionString.from_string('    Key   =   value   ;')
        self.assertEqual(obj['Key'], 'value')

    def test_5(self):
        """
        Double equal signs are converted to one in the key

        """
        obj = ConnectionString.from_string('Key==2=value;')
        self.assertEqual(obj['Key=2'], 'value')

    def test_6(self):
        """
        Keys are properly formatted

        """
        obj = ConnectionString.from_string('cool key  =value;')

        assert 'Cool Key' in obj.get_string()

        # Now with another key formatter
        class ConnStr2(ConnectionString):
            _format_key = staticmethod(lambda k: k.upper())

        obj = ConnStr2.from_string('key=value;')
        self.assertTrue('KEY' in obj.get_string())

    def test_7(self):
        """
        Keys are formatted before look up

        """
        obj = ConnectionString.from_string('key=value;')

        self.assertEqual(obj['kEY'], 'value')

    def test_8(self):
        """
        Value starting with = and properly quoted, is read properly

        """
        obj = ConnectionString.from_string('key="=value" ;')
        self.assertEqual(obj['key'], '=value')

    def test_9(self):
        """
        Connection strings without trailing ';' are also processed

        """
        obj = ConnectionString.from_string('huehue=troll')
        self.assertEqual(obj['huehue'], 'troll')

    def test_10(self):
        """
        Double quotes in literals are converted to one (escaping system)

        """
        obj = ConnectionString.from_string('huehue="troll\'s friend name is ""johnny"""  ;key2 =  value')
        self.assertEqual(obj['huehue'], 'troll\'s friend name is "johnny"')
        self.assertEqual(obj['key2'], 'value')

    def test_11(self):
        """
        Exposed methods of storage work fine

        """
        obj = ConnectionString.from_string('Huehue=troll;')

        self.assertEqual(len(obj), 1)
        self.assertTrue('Huehue' in obj)
        self.assertEqual('troll', obj.get('Huehue'))
        self.assertEqual('default', obj.get('wrong key', 'default'))

    def test_12(self):
        """
        Loading an empty string produces an empty ConnectionString object

        """
        obj = ConnectionString.from_string('')
        assert len(obj) == 0

    def test_13(self):
        """
        Casting the ConnectionString object to unicode/string returns the connection string

        """
        con_string = 'Huehue=troll;'
        obj = ConnectionString.from_string(con_string)

        self.assertEqual(str(obj), con_string)

        # Make the test py3k compatible
        try:
            self.assertEqual(unicode(obj), con_string)
        except NameError:
            pass

    def test_14(self):
        """
        Copying works

        """
        obj = ConnectionString.from_string('Huehue=troll;')
        obj2 = obj.copy()

        self.assertEqual(str(obj), str(obj2))

    def test_15(self):
        """
        Update works with other ConnectionString object

        """
        obj = ConnectionString.from_string('Huehue=troll;')
        obj2 = ConnectionString.from_string('Waldo=faldo;')

        obj.update(obj2)
        self.assertEqual(obj['Waldo'], 'faldo')

    def test_16(self):
        """
        Update works with a standard dict

        """
        obj = ConnectionString.from_string('Huehue=troll;')
        d = {'huehue': 'shutupandtakemymoney'}

        obj.update(d)
        self.assertEqual(obj['Huehue'], 'shutupandtakemymoney')

    def test_17(self):
        """
        Update works with a iterable of key-values

        """
        obj = ConnectionString.from_string('Huehue=troll;')
        d = {'huehue': 'shutupandtakemymoney'}

        obj.update(d.items())
        self.assertEqual(obj['Huehue'], 'shutupandtakemymoney')

    def test_18(self):
        """
        Creating from dictionary works

        """
        d = {'huehue': 'troll'}
        obj = ConnectionString.from_dict(d)

        self.assertEqual(obj['Huehue'], 'troll')

    def test_19(self):
        """
        Creating from iterable works

        """
        d = {'huehue': 'troll'}
        obj = ConnectionString.from_iterable(d.items())

        self.assertEqual(obj['Huehue'], 'troll')

    def test_20(self):
        """
        Deleting works

        """
        obj = ConnectionString.from_dict({'huehue': 'troll'})
        assert 'huehue' in obj
        del obj['huehue']
        assert 'huehue' not in obj

    def test_21(self):
        """
        Invalid connection strings are rejected

        """
        invalid_strs = [
            'key==value;',
            'key="value;',
            'key=\'value;',
            'key=val;ue;',
            'key="hey"there";',
            "key='hey'there';",
        ]

        for s in invalid_strs:
            with self.assertRaises(ValueError):
                ConnectionString.from_string(s)

    def test_23(self):
        """
        Star unpacking works

        """
        obj = ConnectionString.from_string('Provider=someone;User=bartolo;')
        self.assertEqual((lambda **kw: kw)(**obj), {'Provider': 'someone', 'User': 'bartolo'})

    def test_24(self):
        """
        When instantiating from a dictionary, spaces are preserved

        """
        d = {
            'User Id': '  gertrud',
            'Initial Catalog': 'abc  ',
        }
        obj = ConnectionString.from_dict(d)

        for key, value in d.items():
            self.assertEqual(obj[key], value)

    def test_25(self):
        """
        Connection string object is directly iterable

        """
        obj = ConnectionString.from_string('Provider=someone;User=bartolo;')
        self.assertEqual(list(obj), ['Provider', 'User'])

    def test_26(self):
        """
        Comparison works fine

        """
        obj1 = ConnectionString.from_string('Provider=someone;User=bartolo;')
        obj2 = ConnectionString.from_iterable(obj1.items())
        self.assertEqual(obj1, obj2)

        obj2['timeout'] = '78'
        assert obj1 != obj2
        assert obj2 != obj1

    def test_27(self):
        """
        Simple translation works. Formatting is irrelevant

        """
        obj = ConnectionString.from_string('User=bartolo;')
        obj.translate({'USER': 'usr'})
        self.assertEqual(obj['usr'], 'bartolo')

    def test_28(self):
        """
        After calling .translate in strict mode, only keys existing in the translation
        dictionary stay after the process

        """
        obj = ConnectionString.from_string('User=bartolo;key2=val2;')
        obj.translate({'USER': 'usr'})
        self.assertEqual(obj['usr'], 'bartolo')
        assert 'key2' not in obj

    def test_29(self):
        """
        After calling .translate in non strict mode, keys not existing in the translation
        dictionary still exist after the process

        """
        obj = ConnectionString.from_string('User=bartolo;key2=val2;')
        obj.translate({'USER': 'usr'}, strict=False)

        assert len(obj) == 2
        self.assertEqual(obj['usr'], 'bartolo')
        self.assertEqual(obj['key2'], 'val2')
