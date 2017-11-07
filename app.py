from dorm.dorm import DORM

if __name__ == '__main__':
    d = DORM()
    d.create_node("a4731986c84e", name='dorm', host="172.21.0.2")
    n  = list(d._node_store.values()).pop()
    b = n.driver.discover()
    d = []
    col_names = [c.name for c in b.description]
    for col in b.fetchall():
        d.append(dict(zip(col_names, col)))
