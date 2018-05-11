from dorm import models

class User(models.Model): # payments
    id = models.PrimaryKey()
    city = models.Varchar()


class Payment(models.Model):
    id = models.PrimaryKey()
    user =  models.ForeignKey(User)
    amount = models.Integer(User)
