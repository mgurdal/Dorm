import unittest
from unittest.mock import MagicMock, patch

import models


class ModelTestCase(unittest.TestCase):
    """ test base descriptor """

    def setUp(self):
        class Model(models.Model):
            pass

        setattr(self, 'Model', Model)
        self.model = Model(_id=0)

    def test_model_create_in_success(self):
        model = self.model
        self.assertEqual(self.Model.__class__.__name__, 'model_meta')
        self.assertTrue(hasattr(model, '__signature__'))
        self.assertTrue(hasattr(model, '__fields__'))

    @patch('drivers.Sqlite')
    def test__insert_with_sqlite(self, Sqlite):
        """ write the other cases """
        model = self.model
        db = Sqlite()
        model._insert(db, 'sql')
        db.execute.assert_called_with('sql')

    @patch('drivers.Sqlite')
    def test__insert_with_sqlite(self, Sqlite):
        """ write the other cases """

        model = self.model

        db = Sqlite()
        model._insert = MagicMock()

        model.save(db)
        model._insert.assert_called_with(
            db, 'insert into Model(_id) values(0);')
        # test with fields too

    @patch('drivers.Sqlite')
    def test_save_with_sqlite(self, Sqlite):
        """ write the other cases """

        model = self.model

        db = Sqlite()
        model._insert = MagicMock()

        model.save(db)
        model._insert.assert_called_with(
            db, 'insert into Model(_id) values(0);')
        # test with fields too

class BaseNodeTestCase(unittest.TestCase):
    """ test base descriptor """

    def test_base_node_creation(self):
        node = models.BaseNode()
        self.assertTrue(hasattr(node, '_id'))

if __name__ == '__main__':
    unittest.main()
