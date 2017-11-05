from dorm import Node, DORM
from drivers import Sqlite

if __name__ == '__main__':
	d = DORM()
	d.initialize_nodes()
	d.collect_nodes()
	#towns = d.find('Towns').select().all()
