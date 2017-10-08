import models
from drivers import Sqlite
from datetime import datetime
from pprint import pprint as print

class Node(object):
    """
    Node
        'binds to' drivers
        'connects to' databases
        'generates' models
    """
    _models = {}
    _model_store = []

    def __init__(self, ip="0.0.0.0", port=0, name='mysqlite2', user='sky', password='123', type_='sqlite'):
        self.ip = ip
        self.port = port
        self.name = name
        self.user = user
        self.password = password
        self.type_ = type_

    def bind(self, driver):
        # check if supported
        self.driver = driver

    def collect_models(self):
        assert hasattr(self, 'driver'), 'Node does not have a driver'
        model_structures = self.driver.discover()
        ms = []
        for model_s in model_structures:
            # can be dynamic (using from dict or smt.)
            fs = [models.Field.from_dict(x, registery=self._models) for x in model_s['columns']]
            mod = models.model_meta(model_s['table_name'], (models.Model,), {f.name:f for f in fs})
            # handle relation in here via fields referance info

            mod._node = self
            mod._shape = model_s
            ms.append(mod)
            self._models[mod.__name__] = mod
            self._model_store.append(model_s)

        for model_name, model in self._models.items():
            for name, field in model.__fields__.items():
                if type(field) is models.ForeignKey and (len(field.to_table.__fields__) != len(self._models[field.to_table.__name__].__fields__)):
                    self._models[model_name].__fields__.update({name:models.ForeignKey(self._models[field.to_table.__name__])})
        return ms

    def add_model(self, *models):
        assert hasattr(self, 'driver'), 'Node does not have a driver'
        for model in models:
            self.driver.create_table(model)

    def save_model(self, *model_batch):
        assert hasattr(self, 'driver'), 'Node does not have a driver'

        base_query = 'insert into {tablename}({columns}) values{batch};'
        value_batch = []
        for model in model_batch:
            columns = []
            values = []

            for field_name, field_model in model.__fields__.items():
                if hasattr(model, field_name) and not isinstance(getattr(model, field_name), models.Field):
                    values.append(field_model._format(getattr(model, field_name)))
                    columns.append(field_name)

            value_batch.append(",".join(values))
            # print(values)
        sql = base_query.format(
            tablename=model.__class__.__name__,
            columns=', '.join(columns),
            batch=",".join(map(lambda x:"({})".format(x), value_batch))
        )
        cursor = self.driver.execute(sql)

        # validate that its really added to database
        assert cursor, "Could not add to database"
        self.driver.commit()

    def save_node(self, driver):
        assert hasattr(self, 'driver'), 'Node does not have a driver'

        base_query = 'insert into {tablename}({columns}) values({batch});'
        value_batch = []
        values = []
        columns = []
        for field_name, field_model in self.__fields__.items():
            if hasattr(self, field_name) and not isinstance(getattr(self, field_name), models.Field):
                values.append(field_model._format(getattr(self, field_name)))
                columns.append(field_name)

        sql = base_query.format(
            tablename=self.__class__.__name__,
            columns=', '.join(columns),
            batch=", ".join(values)
        )
        cursor = driver.execute(sql)
        # validate that its really added to database
        assert cursor, "Could not add to database"
        driver.commit()

class ModelQuery(dict):
    """
        q1 ^ q2
        q.select('f')...
        takes models and filters them accordingly
        act like models when chaining queries
        acts like sets when doing math operations
        also supports model queries with class methods
    """

    #_nodes = []
    _models = {}
    _queries = []

    @classmethod
    def select(cls, *args, **kwargs):
        """ Lazy select
            Cool loading
            Async
        """
        for n_name, model in cls._models.items():
            cls._queries.append(model.select(*args, **kwargs))
        return cls

    @classmethod
    def all(self):
        # write async
        while self._queries:
            sq = self._queries.pop()
            yield [*sq.all()] # bad

class DORM(object):
    """
        n1 = Node(ip="0.0.0.0", port=0, name='mysqlite', user='sky', password='123', type_='sqlite')
        sq1 = Sqlite(name='test-2.3.sqlite')
        n1.bind(sq1)

        d = DORM()
        d.discover_nodes()
        d.find("User").select('name').all()
    """

    _ext_table = Sqlite(name='conf.db')
    _node_store = {}
    def initialize_nodes(self, nodes=None):
        # support batch insert
        for node in nodes:
            self._ext_table.create_table(node)

    def add_node(self, n):
        # n.save_node(self._ext_table)
        n.collect_models()
        self._node_store[n.name] = n
        pass

    @classmethod
    def find(self, target_model):
        """
        # does it fight with other nodes
        # does it fight with other models
        # if I say get name dont get name
            column from all models

        # I dont care about nodes just gimme the data!
        # select models(tables) and Q on 'em

        d.find('model').select('field')
        """
        # can be changed with SelectQuery
        mq = ModelQuery()
        for n_name, node in self._node_store.items():
            for m_name, model in node._models.items():
                if m_name == target_model:
                    # might need to change to id or auto assigned name
                    mq._models[n_name] = model
        # reduce node store - done
        # find model - done
        # execute q
        # collect & merge
        return mq # node collection

    def collect_nodes(self):
        # check if conf.db exists
        # check if conf.py exists
        # check if cong.json exists
        # health_check
        pass

    def add_model(self, m, to_node):
        # where to put
        # find nodes that contains related tables
        # health_check
        # size check
        # create table
        pass

    def health_check(self):
        pass

    def replication_check(self):
        pass

    def clone_node(self, from_node, to_node):
        pass

    def clone_model(self, model, from_node, to_node):
        pass

if __name__ == '__main__':
    import sys, os

    if sys.argv[1] == "add":
        sys.stdout.write("\n\tAdding new Node\n\n")

        n1 = Node(
                ip= input("IP: (0.0.0.0) "),
                port= input("Port: (5432) "),
                name= input("Name: ({}) ".format(os.uname().nodename)),
                user= input("User: (docker)"),
                password= input("Password: "),
                type_= input("Type: (postgresql) ")
            )
        
    print(n1.ip)
