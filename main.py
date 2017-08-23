import models
from datetime import datetime


class Node(models.BaseNode):
    """
    Node
    'binds to' drivers
    'connects to' databases
    'generates' models
    """
    ip = models.Ip()
    port = models.Integer()
    name = models.Char()
    user = models.Char()
    password = models.Char()
    type_ = models.Char()

    def bind(self, driver):
        # check if supported
        self.driver = driver

    def collect_models(self):
        assert hasattr(self, 'driver'), 'Node does not have a driver'
        return self.driver.discover()

    def save_model(self, model):
        assert hasattr(self, 'driver'), 'Node does not have a driver'
        self.driver.create_table(model)

    def add_model(self, model):
        assert hasattr(self, 'driver'), 'Node does not have a driver'
        model.save(self.driver)

class User(models.Model):
    name = models.String()
    email = models.String()
    age = models.Integer()
    passwd = models.Integer()
    pub = models.Datetime()

if __name__ == '__main__':
    from drivers import Sqlite
    n = Node(ip="0.0.0.0", port=0, name='mysqlite', user='sky', password='123', type_='sqlite')
    u = User(_id=1, name="mehmet", email="mgurdal@protonmail.com", age=23, passwd=123, pub=datetime.now())
    sq = Sqlite(name='hello.db')
