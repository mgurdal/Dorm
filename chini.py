from main import Node
from drivers import Sqlite
n1 = Node(ip="0.0.0.0", port=0, name='mysqlite', user='sky', password='123', type_='sqlite')
sq1 = Sqlite(name='test-2.3.sqlite')
n1.bind(sq1)

n2 = Node(ip="0.0.0.0", port=0, name='mysqlite2', user='sky', password='123', type_='sqlite')
sq2 = Sqlite(name='test-network-2.3.sqlite')
n2.bind(sq2)


n3 = Node(ip="0.0.0.0", port=0, name='mysqlite2', user='sky', password='123', type_='sqlite')
sq3 = Sqlite(name='chinook.db')
n3.bind(sq3)
