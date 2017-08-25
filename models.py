"""
Define models here.
"""


import re
from inspect import Signature, Parameter
from collections import OrderedDict
from pprint import pprint

from queries import *


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

    def __init__(self, name=None):
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
        return '{0} {1}'.format(name, self.ty)

    @classmethod
    def from_dict(cls, kwargs):
        {'fk': False, 'name': '_id',
        'null': False, 'pk': True, 'type': 'INTEGER'}
        if kwargs['pk'] is True:
            field_cls = PrimaryKey()
            field_cls.name = kwargs['name']
            return field_cls
        else:
            field_cls = FIELD_MAP[kwargs['type']]()
            field_cls.name = kwargs['name']
            return field_cls

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

    def __str__(self, data, format='%Y-%m-%d %H:%M:%S.%f'):
        return data.strftime(format)


class Date(Field):
    ty = 'DATETIME'

    def _format(self, data):
        return "'{0}'".format(str(data))

    def __str__(self, data, format='%Y-%m-%d'):
        return data.strftime(format)


class Ip(Char):
    def _format(self, data):
        assert IP_RE.match(data), 'Be sure you were given a valid IP address'
        return super(IP, self)._format(data)


class PrimaryKey(Integer):

    def _sql(self, name, null=False):
        return '{0} {1} NOT NULL PRIMARY KEY'.format(name, self.ty)


class ForeignKey(Integer):

    def __init__(self, to_table):
        self.to_table = to_table
        super(ForeignKey, self).__init__()

    def _sql(self, name):
        return '{column_name} {column_type} NOT NULL REFERENCES {tablename} ({to_column})'.format(
            column_name=name,
            column_type=self.ty,
            tablename=self.to_table.__tablename__,
            to_column='_id'
        )

    def _format(self, data):
        """sql query format of data"""
        if isinstance(data, Model):
            return str(data._id)  # find the pk
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
            '_id': PrimaryKey(),
            from_model.__name__+'_id': ForeignKey(from_model.__class__),
            self.to_model.__name__+'_id': ForeignKey(self.to_model.__class__)
        }
        mm_model = type(mm_table_name, (Model,), foreign_fields)

        return mm_model

FIELD_MAP = {
    'INTEGER': Integer,
    'DOUBLE': Float,
    'CHAR': Char,
    'VARCHAR': Varchar,
    'TEXT': String,
    'FOREIGN': ForeignKey,
    'DATE': Date,
    'DATETIME': Datetime
}

class model_meta(type):
    @classmethod
    def __prepare__(cls, name, bases):
        return OrderedDict()

    def __new__(cls, clsname, bases, clsdict):

        if '_id' not in clsdict:
            clsdict['_id'] = PrimaryKey()

        fields = OrderedDict([(key, val) for key, val in clsdict.items()
                              if isinstance(val, Field)])

        clsobj = super().__new__(cls, clsname, bases, dict(clsdict))

        sign = make_signature(fields)
        setattr(clsobj, "__signature__", sign)
        setattr(clsobj, '__fields__', fields)
        return clsobj


def make_signature(fields):
    return Signature(Parameter(name, Parameter.POSITIONAL_OR_KEYWORD) for name in fields)


class BaseNode(metaclass=model_meta):
    def __init__(self, *args, **kwargs):
        if '_id' not in kwargs:
            # auto incremented
            kwargs.update({'_id':id(self)})
        bound = self.__signature__.bind(*args, **kwargs)
        for key, value in bound.arguments.items():
            setattr(self, key, value)

class Node(BaseNode):

    def connect(self):
        pass

class Model(metaclass=model_meta):
    def __init__(self, *args, **kwargs):
        if '_id' not in kwargs:
            # auto incremented
            kwargs.update({'_id':id(self)})

        bound = self.__signature__.bind(*args, **kwargs)
        for key, value in bound.arguments.items():
            setattr(self, key, value)

    def get(self, **kwargs):
        return SelectQuery(model=self).where(**kwargs).first()

    def select(self, *args, **kwargs):
        return SelectQuery(*args, model=self, **kwargs)

    def update(self, *args, **kwargs):
        return UpdateQuery(*args, model=self, **kwargs)

    def delete(self, *args, **kwargs):
        return DeleteQuery(*args, model=self, **kwargs)

    def __str__(self):
        return "{} : {}".format(self.__class__.__name__, self.__signature__)

    def __repr__(self):
        return "{} : {}".format(self.__class__.__name__, self.__signature__)

    def _insert(self, db, sql):

        cursor = db.execute(sql)
        assert cursor, "Could not add to the database"
        db.commit()

        # refered fields

    def save(self, db=None):
        base_query = 'insert into {tablename}({columns}) values({items});'
        columns = []
        values = []

        for field_name, field_model in self.__fields__.items():
            if hasattr(self, field_name) and not isinstance(getattr(self, field_name), Field):
                values.append(field_model._format(
                    getattr(self, field_name)))
                columns.append(field_name)

        sql = base_query.format(
            tablename=self.__class__.__name__,
            columns=', '.join(columns),
            items=', '.join(values)
        )
        self._insert(db, sql)
