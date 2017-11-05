import sys, os, requests
import docker as Docker
from threading import Thread

class DormClient(object):
    """docstring for DormClient."""
    docker = Docker.from_env()
    sess = requests.Session()
    base_url = "http://0.0.0.0:1307"

    def create_node(self, type_="postgres", replica=False):
        # spin a docker container
        new_container = self.docker.containers.run("mgurdal/dorm", network="dorm_net", ports={'1307': 1307}, detach=True)
        Thread(target=new_container.exec_run, args=("python3.5 service.py",)).start()
        print("NAME:", new_container.name)
        # ip = self.docker.networks.get('dorm_net').attrs['Containers'][new_container.id]['IPv4Address']
        # # pass to dorm
        data={"container_id":new_container.id, "ip":ip, "name":new_container.name, "type_":"postgres", "replica":False}
        self.sess.post(self.base_url+"/create_node/", data=data)
        return new_container

if __name__ == '__main__':
    dc = DormClient()
    n = dc.create_node()
