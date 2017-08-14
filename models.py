
from inspect import Signature, Parameter

def make_signature(fields):
    return Signature(Parameter(name, Parameter.POSITIONAL_OR_KEYWORD) for name in fields)

from collections import OrderedDict

class Descriptor:
    def __init__(self, name=None):
        self.name = name
    
    def __set__(self, instance, value):
        print("set", value)
        instance.__dict__[self.name]=value
        
    def __delete__(self, instance):
        print("del", self.name)
        del instance.__dict__[self.name]
        
class Field(Descriptor):
    ty = ""
    def __set__(self, instance, value):
        return super().__set__(instance, value)

    @property
    def _sql(self):
        """Return sql statement for create table."""
        return '{0} {1}'.format(self.name, self.ty)

class Integer(Field):
    ty = 'INTEGER'

    def _format(self, data):
        """sql query format of data"""
        return str(int(data))     

class String(Field):
    ty = 'TEXT'

    def _format(self, data):
        """sql query format of data"""
        return "'{0}'".format(str(data))

class Float(Field):
    ty = 'DOUBLE'
    def _format(self, data):
        """sql query format of data"""
        return str(float(data))  

class Char(Field):
    ty = 'CHAR'

    def _format(self, data):
        """sql query format of data"""
        return "'{0}'".format(str(data))

class Varchar(Field):
    ty = 'VARCHAR'

    def _format(self, data):
        """sql query format of data"""
        return "'{0}'".format(str(data))

class Datetime(Field):
    ty = 'DATETIME'
    
    def _format(self, data):
        """sql query format of data"""
        return "'{0}'".format(str(data))

    def _format(self, data):
        return "'{0}'".format(str(data))

    def __str__(self, data, format='%Y-%m-%d %H:%M:%S.%f'):
        return data.strftime(format)

class Date(Field):
    ty = 'DATETIME'
    
    def _format(self, data):
        return "'{0}'".format(str(data))
    
    def __str__(self, data, format='%Y-%m-%d'):
        return data.strftime(format)

class PrimaryKey(Integer):

    @property
    def _sql(self):
        return '{0} {1} NOT NULL PRIMARY KEY'.format(self.name, self.ty)

class ForeignKey(Integer):

    def __init__(self, to_table):
        self.to_table = to_table
        super(ForeignKey, self).__init__()
    
    @property
    def _sql(self):
        return '{column_name} {column_type} NOT NULL REFERENCES {tablename} ({to_column})'.format(
            column_name=self.name,
            column_type=self.ty,
            tablename=self.to_table.__name__,
            to_column='_id'
        )

    def _format(self, data):
        """sql query format of data"""
        if isinstance(data, Model):
            return str(data.id)  # find the pk
        else:
            return super(ForeignKey, self)._format(data)


class model_meta(type):
    @classmethod
    def __prepare__(cls, name, bases):
        return OrderedDict()
    
    def __new__(cls, clsname, bases, clsdict):
        fields = {key:val for key, val in clsdict.items() 
                  if isinstance(val, Field)}
        for name in fields:
            clsdict[name].name = name
            
        clsobj = super().__new__(cls, clsname, bases, dict(clsdict))
        sign = make_signature(list(fields.keys()))
        setattr(clsobj, "__signature__", sign)
        setattr(clsobj, '__fields__', fields)
        return clsobj

class Model(metaclass=model_meta):

    def __init__(self, *args, **kwargs):
        bound = self.__signature__.bind(*args, *kwargs)
        for key, value in bound.arguments.items():
            setattr(self, key, value)

    def get(cls, **kwargs):
        return SelectQuery(cls).where(**kwargs).first()

    def select(self, *args, nodes=[]):
        return SelectQuery(model=self, nodes=nodes)

    def update(self, *args, **kwargs):
        return UpdateQuery(self, *args, **kwargs)

    def delete(cls, *args, **kwargs):
        return DeleteQuery(cls, *args, **kwargs)

    def __str__(self):
        return str(vars(self))

    def __repr__(self):
        return str(vars(self))

    def _insert(self, db, sql):
        try:
            cursor = db.execute(sql)
            if isinstance(cursor, str):
                print("Could not add to the {}. {}".format(db.database, cursor))
            else:
                self.id = cursor.lastrowid
        
        except OperationalError as ox:
            print("Table not found in " + db.conf['name'])
            raise ox
            
        finally:
            db.commit()

        # refered fields

    def save(self, db=None):
        base_query = 'insert into {tablename}({columns}) values({items});'
        columns = []
        values = []

        for field_name, field_model in self.__fields__.items():
            if hasattr(self, field_name) and not isinstance(getattr(self, field_name), Field):
                values.append(field_model.sql_format(
                    getattr(self, field_name)))
                columns.append(field_name)

        sql = base_query.format(
            tablename=self.__class__.__name__,
            columns=', '.join(columns),
            items=', '.join(values)
        )
        
        self._insert(db, sql)