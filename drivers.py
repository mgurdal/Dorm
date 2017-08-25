import sqlite3
from models import ManyToMany
from parse import parse

class BaseDriver(object):
    def __init__(self, conn):
        super(BaseDriver, self).__init__()
        self.conn = conn
        self.__tables__ = {}

    def create_table(self, model):
        tablename = model.__class__.__name__
        # Bug in here, foreign key does not work properly
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
        tablename = model.__class__.__name__
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
            print(vars(e))

class Sqlite(BaseDriver):
    def __init__(self, **conf):
        self.conn = sqlite3.connect(database=conf['name'],
                                    detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES
                                    )
        super(Sqlite, self).__init__(conn=self.conn)

    def discover(self):
        """ Creates model structure from database tables """

        table_list = []
        q = "SELECT sql FROM sqlite_master;"
        tables = self.execute(q).fetchall()
        for table in tables:
            if table[0] == None:
                continue

            table_parser = parse(
                'CREATE TABLE {table_name} ({columns})', table[0])
            fs = table_parser.named['columns'].split(', ')
            columns = []
            for field in fs:
                field_parser = parse('{name} {type} {rest}', field) or parse(
                    '{name} {type}', field)
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
                                "{related_table} ({related_field})", table_str).named
                            field_parser.named['related_table'].update(related_table)
                        del field_parser.named['rest']
                    columns.append(field_parser.named)

            table_parser.named['columns'] = columns
            table_list.append(table_parser.named)
        return table_list
