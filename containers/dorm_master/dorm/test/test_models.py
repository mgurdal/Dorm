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

class BaseNodeTestCase(unittest.TestCase):
    """ test base descriptor """

    def test_base_node_creation(self):
        node = models.BaseNode()
        self.assertTrue(hasattr(node, '_id'))

if __name__ == '__main__':
    unittest.main()
