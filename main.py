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

    def models(self):
        pass

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
    
