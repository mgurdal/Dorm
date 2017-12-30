
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
        cs = ""
        try:
            cs = 'create table if not exists {0}({1});'.format(
                tablename, create_sql)

            self.execute(cs, commit=True)
        except Exception as e:
            print(e, cs)

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

    def generate(self, path="", node_name="models", save=True):
        """ Generates model class code from model structre
        """

        class_str = """class {name}(models.Model):\n"""
        field_str = """    {name} = models.{field}({extras})"""
        code = "from dorm.database import models\n\n"
        models = []
        for model_structure in self.discover():

            model = class_str.format(
                name=model_structure['table_name'].title())

            fields = []
            for column in model_structure['columns']:
                if column['extras']['fk']:
                    del column['extras']['fk']
                    del column['extras']['pk']
                    del column['extras']['not_null']
                    if column['extras']['related_field'] == 'id':
                        del column['extras']['related_field']
                    related_table = column['extras'].pop('related_table')
                    if column['extras']:
                        field = field_str.format(
                            name=column['name'], field='ForeignKey', extras=related_table.capitalize() + ', {}')
                    else:
                        field = field_str.format(
                            name=column['name'], field='ForeignKey', extras=related_table.capitalize())

                elif column['extras']['pk']:
                    del column['extras']['pk']
                    del column['extras']['fk']
                    del column['extras']['not_null']

                    if column['extras']:
                        field = field_str.format(
                            name=column['name'], field='PrimaryKey', extras=str(column['extras']))
                    else:
                        field = field_str.format(
                            name=column['name'], field='PrimaryKey', extras='')

                    fields.insert(0, field)
                    continue
                else:
                    del column['extras']['pk']
                    del column['extras']['fk']
                    field = field_str.format(name=column['name'],
                                             field=column['type'].capitalize(
                    ),  # extras=", ".join(k+"="+str(v) for k, v in column['extras'].items())
                        extras='{}')

                fields.append(field.format(str(", ".join(["{}={}".format(x, y) for x, y in column['extras'].items()]) or '')))
            # define primary key first, looks ugly

            # fields.insert(0, fields.pop(fields.index(next(filter(lambda x: "pk=True" in x, fields)))))
            model += "\n".join(fields) + "\n\n"

            models.append(model)
        code += "\n".join(models)
        # find current dir
        import os
        if not os.path.exists(path):
            os.makedirs(path)
        open(path + node_name + ".py", 'w').write(code)
        return models

    def execute(self, sql, commit=True):
        try:
            cursor = self.conn.cursor()
            cursor.execute(sql)
            if commit:
                self.commit()
            return cursor
        except Exception as e:
            print(str(e))
            raise e

class Sqlite(BaseDriver):
    def __init__(self, **conf):
        import sqlite3
        self.conn = sqlite3.connect(database=conf['user'],
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
                            related_table = parse(
                                "{table_name} ({field_name})", table_str).named
                            # this might not set related table properly
                            if 'related_table' in field_parser.named.keys():
                                field_parser.named['related_table'].update(related_table)
                            else:
                                field_parser.named['related_table'] = related_table
                        del field_parser.named['rest']
                        #print("Field\n\r\t", field)
                        #print("Parsed:\n\r\t", field_parser.named)
                    columns.append(field_parser.named)

            table_parser.named['columns'] = columns
            table_list.append(table_parser.named)
        return table_list


class Postgres(BaseDriver):

    def __init__(self, dbname="dorm", user="postgres", host="0.0.0.0", password="docker"):
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
        self.connect(dbname, host, user, password)
        super(Postgres, self).__init__(conn=self.conn)

    def connect(self, dbname, host, user, password):
        import psycopg2 as postgres
        self.conn = postgres.connect(dbname=dbname, host=host, user=user, password=password)
        return self.conn

    def discover(self):
        """ Creates model structure from database tables
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
        fks = self.execute(cs_sql)
        forigns = to_dict(fks)
        fors = [x['column_name'] for x in forigns if x['constraint_name'].endswith("_fkey")]


        f_sql = """select * from INFORMATION_SCHEMA.COLUMNS where table_schema!='pg_catalog' and table_schema!='information_schema'"""
        fields_c = self.execute(f_sql)
        fields = to_dict(fields_c)
        # c+=fields

        structures =  []
        t_names = set(([col['table_name'] for col in fields]))

        structures = [{ "table_name": t_name, "columns": [] } for t_name in t_names]

        for col in fields:
           for table in structures:
              if col['table_name'] == table['table_name']:
                 nc = {}
                 extras = dict(pk=False, fk=False, not_null=False)
                 nc['extras']=extras
                 if col['column_name'] == "id":
                    nc.update(name="id", type="Integer")
                    nc['extras'].update(pk=True, not_null=False)
                    table['columns'].append(nc)
                 else:
                    nc.update(
                       name=col['column_name'],
                       type=col['data_type'].split()[0].title(),
                       extras=dict(
                           fk=False,
                           pk=False
                           )
                    )
                    if col['character_maximum_length']:
                        nc['extras'].update(size=col['character_maximum_length'])
                    if col['is_nullable'] == "YES":
                       nc['extras'].update(not_null=True)
                    elif col['is_nullable'] == "NO":
                       nc['extras'].update(not_null=False)
                    if col['column_name'] in fors:
                          nc['extras'].update(
                             fk=True,
                             pk=False,
                             related_field=col['column_name'].split("_")[1],
                             related_table=col['column_name'].split("_")[0]
                          )

                    table['columns'].append(nc)
        return structures
