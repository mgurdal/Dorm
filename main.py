import models
from datetime import datetime

class Dummy(models.Model):
    _id = models.PrimaryKey()

class User(models.Model):
    _id = models.PrimaryKey()
    name = models.String()
    email = models.String()
    age = models.Integer()
    passwd = models.Integer()
    pub = models.Datetime()
    dummy = models.ForeignKey(Dummy)

if __name__ == '__main__':
    d = Dummy(1)
    u = User(1, "mehmet", "mgurdal@protonmail.com", 23, 123, datetime.now(), d)