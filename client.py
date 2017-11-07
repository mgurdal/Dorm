import sys, os, requests
import docker as Docker
from threading import Thread

class DormClient(object):
    """docstring for DormClient."""
    docker = Docker.from_env()
    sess = requests.Session()
    base_url = "http://0.0.0.0:1307"

    def create_node(self, type_="postgres", replica=False):
        # spin a docker DATABASE container
        # set nodes id as database's id
        self.new_container = None
        try:
            self.new_container = self.docker.containers.run("mgurdal/dorm_node", network="dorm_net", ports={'1307': 1307}, detach=True)
        except Exception:
            pass

        # Thread(target=new_container.exec_run, args=("python3.5 service.py",)).start()
        return self.new_container
    def plswork(self):
        ip = self.docker.networks.get('dorm_net').attrs['Containers'][self.new_container.id]['IPv4Address']
        # # pass to dorm
        data={"container_id":self.new_container.id, "ip":ip, "name":self.new_container.name, "type_":"postgres", "replica":False}
        res = self.sess.post(self.base_url+"/create_node/", data=data)
        return res

if __name__ == '__main__':
    dc = DormClient()
    #n = dc.create_node()
