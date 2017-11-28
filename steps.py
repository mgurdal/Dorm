# coding: utf-8
from dorm import dorm
import psycopg2
p = psycopg2.connect(dbname='dorm', host='172.21.0.2', user='docker', password='docker')
p
c = p.cursor()
p.notices
p.status
get_ipython().run_line_magic('pinfo', 'p.status')
p.isexecuting()7
p.isexecuting()
c.connection
c.name
a = c.execute('select * from information_schema.tables;')
c.fetchone()
c.fetchone()
c.fetchone()
c.fetchone()
c.fetchone()
n = Node(_id=123, ip='172.21.0.2')
n = dorm.Node(_id=123, ip='172.21.0.2')
n.collect_models()
c = n.driver.execute('select * from information_schema.tables;')
c.fetchone()
c.fetchone()
c.fetchone()
c = n.driver.discover()
c = n.driver.discover()
c.fetchone()
c.fetchone()
c.fetchone()
c.fetchone()
c.fetchone()
c = n.driver.execute('create table Hoe(id INTEGER PRIMARY KEY SERIAL, name VARCHAR(56));')
ct = """CREATE TABLE COMPANY(
   ID INT PRIMARY KEY     NOT NULL,
   NAME           TEXT    NOT NULL,
   AGE            INT     NOT NULL,
   ADDRESS        CHAR(50),
   SALARY         REAL
);"""
c = n.driver.execute(ct)
c = n.driver.rollback()
c = n.driver.execute(ct)
c = n.driver.execute("insert into company values(1, 'data', 12, 'asas, asd', 123.4);")
c = n.driver.execute("select * from company;")
c.fetchall()
c.fetchall()
n.collect_models()
c = n.driver.rollback()
d =  n.driver
d.execute("""select *
from information_schema.tables
where table_schema not in ('pg_catalog', 'information_schema')
and table_schema not like 'pg_toast%'""")
a = d.execute("""select *
from information_schema.tables
where table_schema not in ('pg_catalog', 'information_schema')
and table_schema not like 'pg_toast%'""")
a.fetchone()
a.fetchone()
a.fetchone()
a = d.execute("""select * from company where false;""")
a.fetchone()
a.fetchone()
a.description
a = d.execute("""select table_name
from information_schema.tables
where table_schema not in ('pg_catalog', 'information_schema')
and table_schema not like 'pg_toast%'""")
a = d.execute("""select table_name
from information_schema.tables
where table_schema not in ('pg_catalog', 'information_schema')
and table_schema not like 'pg_toast%'""")
b = a.fetchall()
b
a = d.execute("""select *
from information_schema.columns
where table_schema not in ('pg_catalog', 'information_schema')
and table_schema not like 'pg_toast%'""")
c = a.fetchall()
c
a.description
a
c
v = a.description
v
v[0]
l = v[0]
l.name
l = [x.name for x in v]
l
get_ipython().run_line_magic('save', '1-71 steps')
