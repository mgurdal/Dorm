import docker

from dorm.dorm import DORM
from models import City
# def discoverNodes(client):
#     dorm_net = client.networks.get("dorm_net")
#     nets = [ {
#     "host": x.attrs['NetworkSettings']['Networks']['dorm_net']['IPAddress'],
#     "container_id": hash(x.short_id),
#     "name": x.name
#     } for x in dorm_net.containers ]
#     return nets

if __name__ == '__main__':
    d = DORM()
    d.discover()
