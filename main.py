import models
from datetime import datetime
from pprint import pprint as print

class Node(models.BaseNode):
    """
    Node
    'binds to' drivers
    'connects to' databases
    'generates' models
    """
    _models = {}
    ip = models.Ip()
    port = models.Integer()
    name = models.Char()
    user = models.Char()
    password = models.Char()
    type_ = models.Char()

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
            ms.append(mod)
            self._models[mod.__name__] = mod

        for model_name, model in self._models.items():
            for name, field in model.__fields__.items():
                if type(field) is models.ForeignKey and (len(field.to_table.__fields__) != len(self._models[field.to_table.__name__].__fields__)):
                    self._models[model_name].__fields__.update({name:models.ForeignKey(self._models[field.to_table.__name__])})
        return ms

    def add(self, *models):
        assert hasattr(self, 'driver'), 'Node does not have a driver'
        for model in models:
            self.driver.create_table(model)

    def save(self, *model_batch):
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
            print(values)
        sql = base_query.format(
            tablename=model.__class__.__name__,
            columns=', '.join(columns),
            batch=",".join(map(lambda x:"({})".format(x), value_batch))
        )
        cursor = self.driver.execute(sql)

        # validate that its really added to database
        assert cursor, "Could not add to database"
        self.driver.commit()

class DORM(object):
    """
        n1 = Node(ip="0.0.0.0", port=0, name='mysqlite', user='sky', password='123', type_='sqlite')
        sq1 = Sqlite(name='test-2.3.sqlite')
        n1.bind(sq1)

        n2 = Node(ip="0.0.0.0", port=0, name='mysqlite2', user='sky', password='123', type_='sqlite')
        sq2 = Sqlite(name='test-network-2.3.sqlite')
        n2.bind(sq2)


        n3 = Node(ip="0.0.0.0", port=0, name='mysqlite2', user='sky', password='123', type_='sqlite')
        sq3 = Sqlite(name='chinook.db')
        n3.bind(sq3)
    """
    def initialize_nodes(self):
        pass

    def add_node(self, n):
        pass

    def add_model(self, m):
        pass

    def find(self, q):
        pass

    def get(self, q):
        pass

    def health_check(self):
        pass

    def replication_check(self):
        pass

    def clone_node(self, from_node, to_node):
        pass

    def clone_model(self, model, from_node, to_node):
        pass
