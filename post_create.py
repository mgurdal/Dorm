# coding: utf-8

import psycopg2
from dorm.dorm import Node

cities_table_sql = """CREATE TABLE IF NOT EXISTS cities (
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
        FOREIGN KEY (city_id) REFERENCES cities (id)

);"""

n = Node(1, ip="172.19.0.2")
mr_d = n.driver

mr_d.execute(cities_table_sql)
mr_d.execute(weather_table_sql)

def to_dict(cur):
    names = [x.name for x in cur.description]
    rs = cur.fetchall()
    table_set = [dict(zip(names, x)) for x in rs]
    return table_set

# tables = mr_d.execute("""select *
# from information_schema.tables
# where table_schema not in ('pg_catalog', 'information_schema')
# and table_schema not like 'pg_toast%'""")
# td = to_dict(tables)
# td
# columns = mr_d.execute("""select *
# from information_schema.columns
# where table_schema not in ('pg_catalog', 'information_schema')
# and table_schema not like 'pg_toast%'""")
# cd = to_dict(columns)
# get_ipython().run_line_magic('cd', '')
cs_sql = """select * from INFORMATION_SCHEMA.KEY_COLUMN_USAGE"""
# mr_d.rollback()
fks = mr_d.execute(cs_sql)
forigns = to_dict(fks)
rels, fors = forigns[::2], forigns[1::2]
c = []

for foreign in zip(rels, fors):
    d = foreign[1]
    #  d.update(foreign[1])
    c.append(d)

f_sql = """select * from INFORMATION_SCHEMA.COLUMNS where table_schema!='pg_catalog' and table_schema!='information_schema'"""
fields_c = mr_d.execute(f_sql)
fields = to_dict(fields_c)
# c+=fields

structures =  []
t_names = set(([col['table_name'] for col in c]))
"""{
'table_name': 'Roads',
   'columns': [
               {'fk': False, 'name': 'PK_UID',     'pk': True,  'type': 'INTEGER'},
               {'fk': False, 'name': 'F_NODE',     'pk': False, 'type': 'INTEGER'},
               {'fk': False, 'name': 'T_NODE',     'pk': False, 'type': 'INTEGER'},
               {'fk': False, 'name': 'Type',       'pk': False, 'type': 'TEXT'},
               {'fk': False, 'name': 'Speed',      'pk': False, 'type': 'TEXT'},
               {'fk': False, 'name': 'TravelTime', 'pk': False, 'type': 'DOUBLE'},
               {'fk': False, 'name': 'Geometry', '  pk': False, 'type': 'LINESTRING'}
             ]
}"""

structures = [{ "table_name": t_name, "columns": [] } for t_name in t_names]
from itertools import zip_longest

for col in c:
   for table in structures:
      if col['table_name'] == table['table_name']:
         nc = {}
         if col['column_name'] == "id":
            nc.update(pk=True, fk=False, type="Integer")
            table['columns'].append(nc)
         else:
            nc.update(name=col['column_name'], nullable=col['is_nullable'], type=col['data_type'].split()[0].title(), size=col['character_maximum_length'])
            table['columns'].append(nc)
# fix foreing pkey not matching 
print(structures)
