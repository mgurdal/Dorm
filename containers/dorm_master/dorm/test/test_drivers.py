import unittest
from unittest.mock import MagicMock, patch

from drivers import BaseDriver, Sqlite

class BaseDriverTestCase(unittest.TestCase):

    def test_initialize_driver(self):
        conn = MagicMock()
        base = BaseDriver(conn)

        self.assertTrue(hasattr(base, 'conn'))
        self.assertTrue(hasattr(base, '__tables__'))
        self.assertTrue(isinstance(base.__tables__, dict))

    def test_create_table(self):
        model = MagicMock()
        model.__name__ = "TestTable"
        field = MagicMock()
        field._sql = lambda x: x
        setattr(model, '__fields__', {'test_field': field})

        base = BaseDriver(None)
        base.execute = MagicMock()

        base.create_table(model)

        base.execute.assert_called_with('create table if not exists TestTable (test_field);', commit=True)

    def test_drop_table(self):
        model = MagicMock()
        model.__name__ = "TestTable"
        model.__fields__ = MagicMock()
        base = BaseDriver(None)
        base.execute = MagicMock()

        base.drop_table(model)

        base.execute.assert_called_with('drop table IF EXISTS TestTable;', commit=True)

if __name__ == '__main__':
    unittest.main()
