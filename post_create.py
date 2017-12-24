# coding: utf-8

from itertools import zip_longest
import psycopg2
from dorm.dorm import Node

cities_table_sql = """CREATE TABLE IF NOT EXISTS city (
    id serial primary key,
    city varchar(80),
    location point
)
;"""

weather_table_sql = """CREATE TABLE IF NOT EXISTS weather (
        id        serial primary key,
        city_id   serial,
        temp_lo   int,
        temp_hi   int,
        prcp      real,
        date      date,
        FOREIGN KEY (city_id) REFERENCES city (id)

);"""

n = Node(1, ip="172.19.0.2")
mr_d = n.driver
#
mr_d.execute(cities_table_sql)
mr_d.execute(weather_table_sql)

# fix foreing pkey not matching
