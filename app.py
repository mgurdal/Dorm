import docker

from dorm.dorm import DORM

def discoverNodes(client):
    dorm_net = client.networks.get("dorm_net")
    nets = [ {
    "host": x.attrs['NetworkSettings']['Networks']['dorm_net']['IPAddress'],
    "container_id": hash(x.short_id),
    "name": x.name
    } for x in dorm_net.containers ]
    return nets

if __name__ == '__main__':
    d = DORM()
    client = docker.from_env()
    ns = []
    for n  in discoverNodes(client):
        c = d.create_node(container_id=n['container_id'], ip=n['host'], name=n['name'])
        ns.append(c)
