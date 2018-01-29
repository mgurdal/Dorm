"""
Define models here.
"""


import re
from inspect import Signature, Parameter
from collections import OrderedDict

from .queries import *


"""
Define fields here
"""


IP_RE = re.compile(
    r'^(([0-9]|[1-9][0-9]|1[0-9]{2}|\
    2[0-4][0-9]|25[0-5])\.)\
    {3}([0-9]|[1-9][0-9]|\
    1[0-9]{2}|2[0-4][0-9]|25[0-5])$'
    )

class Descriptor:
    value = None

    def __init__(self, name=None, **kwargs):
        self.name = name

    def __set__(self, instance, value):
        self.value = value
        # instance.__dict__[self.name]
        # instance.__dict__[self.name]=value

    def __get__(self, _, type=None):
        return self.value

    def __delete__(self, instance):
        print("del", self.name)
        self.value = None


class Field(Descriptor):
    ty = ""

    def __set__(self, instance, value):
        return super().__set__(instance, value)

    def _sql(self, name):
        """Return sql statement for create table."""
        size = "("+str(getattr(self, 'size'))+")" if hasattr(self, 'size') else ""
        return '{0} {1}{2}'.format(name, self.ty, size)

    @classmethod
    def from_dict(cls, field, registery={}):
        """
        {'fk': False, 'name': 'id', 'null': False, 'pk': True, 'type': 'INTEGER'}
        """
        if field['extras']['pk'] is True:
            field_cls = PrimaryKey()
            field_cls.name = field['name']
            return field_cls
        elif field['extras']['fk'] is True:
            related_table = field['extras']['related_table']
            # check model registery
            if related_table['table_name'] in registery:
                field_cls = ForeignKey(registery[related_table['table_name']], related_table['field_name'])
            else:
                # print("Model '{}' not found in node registery creating a dummy one.".format(related_table['table_name']))
                field_cls = ForeignKey(model_meta(related_table['table_name'].title(), (Model,), {}), related_table['field_name'])
            field_cls.name = field['name']
            return field_cls
        else:
            field_cls = FIELD_MAP[field['type'].upper()]()
            field_cls.name = field['name']
            return field_cls

class Integer(Field):
    ty = 'INTEGER'
    def _format(self, data):
        """sql query format of data"""
        return str(int(data))


class String(Field):
    ty = 'TEXT'
    size = 80
    def _format(self, data):
        """sql query format of data"""
        return "'{0}'".format(str(data))


class Float(Field):
    ty = 'DOUBLE'
    size = 11
    def _format(self, data):
        """sql query format of data"""
        return str(float(data))


class Char(Field):
    ty = 'CHAR'
    size = 11
    def _format(self, data):
        """sql query format of data"""
        return "'{0}'".format(str(data))

class Character(Field):
    ty = 'CHAR'
    size = 80
    def _format(self, data):
        """sql query format of data"""
        return "'{0}'".format(str(data))

class Varchar(Field):
    ty = 'VARCHAR'
    size = 11
    def _format(self, data):
        """sql query format of data"""
        return "'{0}'".format(str(data))

class Point(Field):
    ty = 'POINT'
    def _format(self, point):
        """sql query format of data"""
        return "Point({0}, {1})".format(str(point[0]), str(point[1]))

class Real(Field):
    ty = 'VARCHAR'

    def _format(self, data):
        """sql query format of data"""
        return "'{0}'".format(str(data))
#
class Datetime(Field):
    ty = 'DATETIME'

    def _format(self, data):
        """sql query format of data"""
        return "'{0}'".format(str(data))

    def __str__(self, data, format='%Y-%m-%d %H:%M:%S.%f'):
        return data.strftime(format)


class Date(Field):
    ty = 'DATE'

    def _format(self, data):
        return "'{0}'".format(str(data))

    def __str__(self, data, format='%Y-%m-%d'):
        return data.strftime(format)


class Ip(Char):
    def _format(self, data):
        #assert IP_RE.match(data), 'Be sure you were given a valid IP address'
        #print(IP_RE.match(data))
        return super(Ip, self)._format(data)


class PrimaryKey(Integer):

    def _sql(self, name, null=False):
        return '{0} {1} NOT NULL PRIMARY KEY'.format(name, self.ty)


class ForeignKey(Integer):

    def __init__(self, to_table=None, to_column='id'):
        self.to_table = to_table
        self.to_column = to_column
        super(ForeignKey, self).__init__()

    def _sql(self, name):
        return '{column_name} {column_type} NOT NULL REFERENCES {tablename} ({to_column})'.format(
            column_name=name,
            column_type=self.ty,
            tablename=self.to_table.__name__,
            to_column=self.to_column
        )

    def _format(self, data):
        """sql query format of data"""
        if isinstance(data, Model):
            return str(data.id)  # find the pk
        else:
            return super(ForeignKey, self)._format(data)


class ManyToMany(object):
    """ Many to Many relation field """

    def __init__(self, to_model=None):
        self.to_model = to_model

    def create_mm_model(self, field_name, from_model, node=None):
        mm_table_name = "MM_{}_{}".format(
            self.to_model.__name__,
            from_model.__name__)

        # find primary keys
        from_model_pk = (k for k, f in from_model.__fields__.items()
                         if isinstance(f, PrimaryKey))
        to_model_pk = (k for k, f in self.to_model.__fields__.items()
                         if isinstance(f, PrimaryKey))

        # merge class attrs
        foreign_fields = {
            'id': PrimaryKey(),
            from_model.__name__+'id': ForeignKey(from_model.__class__),
            self.to_model.__name__+'id': ForeignKey(self.to_model.__class__)
        }
        mm_model = type(mm_table_name, (Model,), foreign_fields)

        return mm_model

FIELD_MAP = {
    'INTEGER': Integer,
    'REAL': Integer,
    'DOUBLE': Float,
    'CHAR': Char,
    'VARCHAR': Varchar,
    'TEXT': String,
    'FOREIGN': ForeignKey,
    'DATE': Date,
    'DATETIME': Datetime,
    'POINT': Point,
    'LINESTRING': Varchar,
    'MULTIPOLYGON': Varchar,
    'BLOB': Varchar,
    'CHARACTER': Character,

}

class model_meta(type):
    def __new__(cls, clsname, bases, clsdict):


        fields = { key: val for key, val in clsdict.items()
                              if isinstance(val, Field)}

        clsobj = super().__new__(cls, clsname, bases, dict(clsdict))
        #
        setattr(clsobj, '__fields__', fields)
        setattr(clsobj, '__relations__', [ f for _, f in fields.items() if type(f) is ForeignKey ])
        # # assign referance for relational fields
        for name, field in fields.items():
            if type(field) is ForeignKey:
                setattr(field.to_table, clsname.lower()+"s", clsobj)
        return clsobj

class Model(metaclass=model_meta):
    def __init__(self, *args, **kwargs):
        self.id = PrimaryKey()
        for key, value in kwargs.items():
            setattr(self, key, value)

    @classmethod
    def get(self, **kwargs):
        return SelectQuery(model=self).where(**kwargs).all()

    @classmethod
    def all(self):
        return SelectQuery(model=self).all()

    @classmethod
    def instance(cls):
        return "{} = {}({})".format(cls.__name__.lower(), cls.__name__, ", ".join("{}='value'".format(x) for x in cls.__fields__))

    # @property
    # def fields(self):
    #     return {k, v.__class__ for k, v in self.__fields__.items()}

    @classmethod
    def select(self, *args, nodes=set(), **kwargs):
        return SelectQuery(*args, model=self, nodes=nodes, **kwargs)

    def update(self, *args, **kwargs):
        return UpdateQuery(*args, model=self, **kwargs)

    def delete(self, *args, **kwargs):
        return DeleteQuery(*args, model=self, **kwargs)


class BaseNode(metaclass=model_meta):
    def __init__(self, *args, **kwargs):
        if 'id' not in kwargs:
            # auto incremented
            kwargs.update({'id':id(self)})
        # wrong update here reference confliction
        for key, value in kwargs.items():
            setattr(self, key, value)
