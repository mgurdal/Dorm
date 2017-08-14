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
    """ Test base field here """
    pass

if __name__ == '__main__':
    unittest.main()