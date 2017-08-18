import unittest
from unittest.mock import MagicMock, patch

import queries


class SelectQueryTestCase(unittest.TestCase):
    """ test base descriptor """
    
    @patch('models.Model')
    @patch('models.Node')
    def test_select_query_initialization_without_args(self, Node, Model):

        stub_model = Model()

        stub_node = Node()
        stub_node.driver = MagicMock() 

        # initialize
        sq = queries.SelectQuery(model=stub_model, nodes=[stub_node])
        
        self.assertEqual(sq.model, stub_model.__class__)
        self.assertEqual(sq.databases, [stub_node.driver])
        self.assertEqual('*', sq.query)
        self.assertEqual('select {columns} from {tablename};', sq.base_sql)

    @patch('models.Model')
    @patch('models.Node')
    def test_select_query_initialization_with_args(self, Node, Model):

        stub_model = Model()

        stub_node = Node()
        stub_node.driver = MagicMock() 

        # initialize
        sq = queries.SelectQuery('test1', 'test2', model=stub_model, nodes=[stub_node])
        
        self.assertEqual(sq.model, stub_model.__class__)
        self.assertEqual(sq.databases, [stub_node.driver])
        self.assertEqual('test1, test2', sq.query)
        self.assertEqual('select {columns} from {tablename};', sq.base_sql)

    @patch('models.Model')
    def test_sql_property_with_args(self, Model):
        sq = queries.SelectQuery('test1', 'test2')
        sq.model = Model()
        sq.model.__name__ = "Test"
        
        self.assertEqual('select test1, test2 from Test;' ,sq.sql)

    @patch('models.Model')
    def test_sql_property_without_args(self, Model):
        sq = queries.SelectQuery()
        sq.model = Model()
        sq.model.__name__ = "Test"
        
        self.assertEqual('select * from Test;' ,sq.sql)

if __name__ == '__main__':
    unittest.main()
