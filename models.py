from dorm import models

class City(models.Model):
    id = models.PrimaryKey()
    city = models.Character(not_null=True, size=80)
    location = models.Point(not_null=True)


class Weather(models.Model):
    id = models.PrimaryKey()
    city_id = models.ForeignKey(City)
    prcp = models.Real(not_null=True)
    date = models.Date(not_null=True)
    temp_hi = models.Integer(not_null=True)
    temp_lo = models.Integer(not_null=True)
