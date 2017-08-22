import models
from datetime import datetime


class Node(models.BaseNode):
    ip = models.Ip()
    port = models.Integer()
    name = models.Char()
    user = models.Char()
    password = models.Char()
    type_ = models.Char()
    

class User(models.Model):
    name = models.String()
    email = models.String()
    age = models.Integer()
    passwd = models.Integer()
    pub = models.Datetime()

if __name__ == '__main__':
    
    u = User(_id=1, name="mehmet", email="mgurdal@protonmail.com", age=23, passwd=123, pub=datetime.now())