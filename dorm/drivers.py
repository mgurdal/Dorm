
from .models import ManyToMany, Model, model_meta
from parse import parse
from pprint import pprint

class BaseDriver(object):
    def __init__(self, conn):
        super(BaseDriver, self).__init__()
        self.conn = conn
        self.__tables__ = {}

    def create_table(self, model):

        #assert type(model) in (Model, model_meta), "Cannot create table with given data structure!"

        tablename = model.__name__

        # Bug in here, foreign key does not work properly
        # new Model class does not fields yet
        create_sql = ', '.join(field._sql(name) for name, field in model.__fields__.items())

        try:
            self.execute('create table if not exists {0} ({1});'.format(
                tablename, create_sql), commit=True)
        except Exception as e:
            print(e, create_sql)

        if tablename not in self.__tables__.keys():
            self.__tables__[tablename] = model

        for field in model.__fields__.values():
            if isinstance(field, ManyToMany):
                field.create_m2m_table()

    def drop_table(self, model):
        tablename = model.__name__
        self.execute('drop table IF EXISTS {0};'.format(
            tablename), commit=True)
        #del self.__tables__[tablename]
        for name, field in model.__fields__.items():
            if isinstance(field, ManyToMany):
                field.drop_m2m_table()

    def commit(self):
        self.conn.commit()

    def rollback(self):
        self.conn.rollback()

    def close(self):
        self.conn.close()

    def execute(self, sql, commit=False):
        print(sql)
        cursor = self.conn.cursor()
        if not cursor:
            print("Invalid sql", sql)
        try:
            cursor.execute(sql)
            if commit:
                print(sql)
                self.commit()
            return cursor
        except Exception as e:
            print("Error")
            print(vars(e))

class Sqlite(BaseDriver):
    def __init__(self, **conf):
        import sqlite3
        self.conn = sqlite3.connect(database=conf['name'],
                                    detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES
                                    )
        super(Sqlite, self).__init__(conn=self.conn)

    def discover(self):
        """ Creates model structure from database tables
            structure example:
            {
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
            }

        """

        table_list = []
        q = "SELECT m.sql FROM sqlite_master as m where m.sql like 'CREATE TABLE %'"
        tables = self.execute(q).fetchall()
        for table in tables:

            if table[0] == None:
                continue
            if "CREATE TABLE" not in table[0]:
                continue
            table_parser = parse(
                'CREATE TABLE {table_name} ({columns})', table[0])
            if not table_parser:
                continue
            fs = table_parser.named['columns'].split(',')
            fs = [c.strip() for c in fs]
            columns = []
            for field in fs:

                field_parser = parse('{name} {type} {rest}', field) or parse(
                    '{name} {type}', field)
                field_parser.named['name'] = field_parser.named['name'].strip().replace("[", "").replace("]", "").replace("\"", "")
                if field_parser is not None:
                    field_parser.named['pk'] = False
                    field_parser.named['fk'] = False
                    # if column does not have argument. e.g CHAR(15)
                    if field_parser.named['type'][-1] == r")":
                        field_parser.named['size']=field_parser.named['type'][field_parser.named['type'].rfind("(")+1:-1]
                        field_parser.named['type'] = field_parser.named['type'][:field_parser.named['type'].rfind("(")]
                    if 'rest' in field_parser.named.keys():
                        if 'NOT NULL' in field_parser.named['rest']:
                            field_parser.named['null'] = False

                        if 'PRIMARY KEY' in field:
                            field_parser.named['pk'] = True

                        if 'REFERENCES' in field_parser.named['rest']:
                            field_parser.named['fk'] = True
                            table_str = field.split(" REFERENCES ")[1]
                            print(table_str)
                            related_table = parse(
                                "{table_name} ({field_name})", table_str).named
                            # this might not set related table properly
                            if 'related_table' in field_parser.named.keys():
                                field_parser.named['related_table'].update(related_table)
                            else:
                                field_parser.named['related_table'] = related_table
                            print(field_parser.named['related_table'])
                        del field_parser.named['rest']
                        #print("Field\n\r\t", field)
                        #print("Parsed:\n\r\t", field_parser.named)
                    columns.append(field_parser.named)

            table_parser.named['columns'] = columns
            table_list.append(table_parser.named)
        return table_list


class Postgres(BaseDriver):

    def __init__(self, dbname="dorm", user="postgres", host="0.0.0.0", password="docker"):
        import psycopg2 as postgres
        # connect to the postgres database inside the docker
        # if this was in the docker and in the same net
        # this would not be an issue
        """
            dbname – the database name (database is a deprecated alias)
            user – user name used to authenticate
            password – password used to authenticate
            host – database host address (defaults to UNIX socket if not provided)
            port – connection port number (defaults to 5432 if not provided)
            adap = postgres.connect(dbname="postgres", user="docker", host="172.21.0.2", password="docker")
        """
        self.conn = postgres.connect(dbname=dbname, host=host, user="docker", password=password)
        super(Postgres, self).__init__(conn=self.conn)

    def discover(self):
        """ Creates model structure from database tables """
        table_info_sql = """SELECT
            f.attnum AS number,
            f.attname AS name,
            f.attnum,
            f.attnotnull AS notnull,
            n.nspname as database,
            c.relname as table_name,
            pg_catalog.format_type(f.atttypid,f.atttypmod) AS type,
            CASE
                WHEN p.contype = 'p' THEN 't'
                ELSE 'f'
            END AS primarykey,
            CASE
                WHEN p.contype = 'u' THEN 't'
                ELSE 'f'
            END AS uniquekey,
            CASE
                WHEN p.contype = 'f' THEN g.relname
            END AS foreignkey,
            CASE
                WHEN p.contype = 'f' THEN p.confkey
            END AS foreignkey_fieldnum,
            CASE
                WHEN p.contype = 'f' THEN g.relname
            END AS foreignkey,
            CASE
                WHEN p.contype = 'f' THEN p.conkey
            END AS foreignkey_connnum,
            CASE
                WHEN f.atthasdef = 't' THEN d.adsrc
            END AS default
        FROM pg_attribute f
            JOIN pg_class c ON c.oid = f.attrelid
            JOIN pg_type t ON t.oid = f.atttypid
            LEFT JOIN pg_attrdef d ON d.adrelid = c.oid AND d.adnum = f.attnum
            LEFT JOIN pg_namespace n ON n.oid = c.relnamespace
            LEFT JOIN pg_constraint p ON p.conrelid = c.oid AND f.attnum = ANY (p.conkey)
            LEFT JOIN pg_class AS g ON p.confrelid = g.oid
        WHERE c.relkind = 'r'::char
            AND f.attnum > 0 ORDER BY number
        ;"""
        return self.execute(table_info_sql, commit=True)