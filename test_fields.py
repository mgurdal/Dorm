import unittest
from unittest.mock import MagicMock, patch

import models


class DescriptorTestCase(unittest.TestCase):
    """ test base descriptor """

    def test_descriptor_initializes_name(self):
        d = models.Descriptor('test')
        self.assertTrue(hasattr(d, 'name'))
        self.assertEqual(d.name, 'test')


class FieldTestCase(unittest.TestCase):
    """Base field object"""

    def setUp(self):
        self.test_field = models.Field('COLUMN_TYPE')

    def test__sql(self):
        """Return sql statement for create table."""

        self.test_field.ty = "COLUMN_TYPE"

        self.assertEqual("test COLUMN_TYPE",
                         self.test_field._sql('test'))

    def test_from_dict(self):
        field_d = {'fk': False, 'name': 'test', 'pk': False, 'type': 'TEXT'}
        field = models.Field.from_dict(field_d)

        self.assertTrue(isinstance(field, models.Field))
        self.assertEqual(type(field), models.String)
        self.assertTrue(hasattr(field, 'name'))
        self.assertEqual(field.name, 'test')


class IntegerTestCase(unittest.TestCase):
    """SQLite Integer field"""

    def setUp(self):
        self.test_int_field = models.Integer()

    def test_column_type(self):
        self.assertEqual('INTEGER', self.test_int_field.ty)

    def test__format(self):
        """sql query format of data"""
        self.assertIsInstance(self.test_int_field._format(20), str)


class FloatTestCase(unittest.TestCase):
    """SQLite Float field"""

    def setUp(self):
        self.test_int_field = models.Float()

    def test_column_type(self):
        self.assertEqual('DOUBLE', self.test_int_field.ty)

    def test__format(self):
        """sql query format of data"""
        self.assertIsInstance(self.test_int_field._format(20.6), str)


class CharTestCase(unittest.TestCase):
    """SQLite Char field"""

    def setUp(self):
        self.test_char_field = models.Char()

    def test__sql(self):
        self.assertEqual('test CHAR', self.test_char_field._sql('test'))

    def test__format(self):
        self.assertEqual("'test'", self.test_char_field._format("test"))


class VarcharTestCase(unittest.TestCase):
    """SQLite Varchar field"""

    def setUp(self):
        self.test_char_field = models.Varchar()

    def test__sql(self):
        self.assertEqual('test VARCHAR',
                         self.test_char_field._sql('test'))

    def test__format(self):
        self.assertEqual("'test'", self.test_char_field._format("test"))
        """
        def test_char_max_length_cannot_be_exceeded(self):
        try:
            self.test_char_field._format("test_ex")
        except Exception as e:
            self.assertEqual('maximum length exceeded', e.args[0])
        """


class StringTestCase(unittest.TestCase):
    """SQLite Text field"""

    def test__format(self):
        """sql query format of data"""
        self.assertEqual("'test'", models.String()._format('test'))


class DatetimeTestCase(unittest.TestCase):

    def setUp(self):
        self.test_Datetime = models.Datetime()

    def test__format(self):
        """sql query format of data"""
        from datetime import datetime
        self.assertEqual("'2017-07-07 00:00:00'",
                         self.test_Datetime._format(datetime(2017, 7, 7, 0, 0, 0)))


class DateTestCase(unittest.TestCase):
    def setUp(self):
        self.test_date = models.Date()

    def test__format(self):
        """sql query format of data"""
        from datetime import date
        self.assertEqual(
            "'2017-07-07'", self.test_date._format(date(2017, 7, 7)))


class TimestampTestCase(unittest.TestCase):

    def setUp(self):
        self.test_timestamp = models.Datetime()

    def test__format(self):
        """sql query format of data"""
        from datetime import datetime
        self.assertEqual("'2017-07-07 00:00:00'",
                         self.test_timestamp._format(datetime(2017, 7, 7, 0, 0, 0)))


class PrimaryKeyTestCase(unittest.TestCase):

    def test__sql(self):
        test_pk = models.PrimaryKey()
        self.assertEqual('test INTEGER NOT NULL PRIMARY KEY',
                         test_pk._sql('test'))


class ForeignKeyTestCase(unittest.TestCase):

    def setUp(self):
        self.to_table = models.Model(_id=1)
        self.to_table.__tablename__ = 'test_table'
        self.test_fk = models.ForeignKey(self.to_table)
        self.test_fk.name = 'test_fk'

    def test__sql(self):
        self.assertEqual(
            'test_fk INTEGER NOT NULL REFERENCES test_table (_id)', self.test_fk._sql('test_fk'))

    def test__format(self):
        """sql query format of data"""
        self.assertEqual("1", self.test_fk._format(self.to_table))


class ManyToManyTestCase(unittest.TestCase):
    """ """

    @patch('models.Model')
    def test_many_to_many_creation(self, Model):
        """ 1- initialize manytomany with stub model
            2- check manytomany has a to_model attribute
        """
        model = Model()
        manytomany = models.ManyToMany(model)

        self.assertTrue(hasattr(manytomany, 'to_model'))

    @patch('models.Node')
    def test_create_relation(self, Node):
        n = Node()
        to_model = MagicMock()
        to_model.__name__ = 'ToModel'
        to_model.__fields__ = {'_id':models.PrimaryKey()}

        from_model = MagicMock()
        from_model.__name__ = 'FromModel'
        from_model.__fields__ = {'_id':models.PrimaryKey()}

        manytomany = models.ManyToMany(to_model)

        mm_model = manytomany.create_mm_model('referance_name', from_model, node=n)

        self.assertEqual(mm_model.mro()[1], models.Model)
        self.assertEqual(mm_model.__name__, "MM_ToModel_FromModel")
        self.assertTrue(hasattr(mm_model, 'FromModel_id'))
        self.assertTrue(hasattr(mm_model, 'ToModel_id'))

        self.assertTrue(type(mm_model.FromModel_id), models.ForeignKey)
        self.assertTrue(type(mm_model.ToModel_id), models.ForeignKey)

        # check if bound tables same with given tables

if __name__ == '__main__':
    unittest.main()
