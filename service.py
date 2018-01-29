"""
REST the DORM in here
"""
import sys
from sanic import Sanic
from sanic.response import json
from dorm.dorm import DORM
from sanic_cors import CORS, cross_origin
from sanic import response
from dorm.system_utils import AFileStream
import socketio
import json as default_json

from sanic import Sanic
from sanic.response import html

import socketio


import json, time
import os, time, asyncio

app = Sanic()
CORS(app)
dorm = DORM()
sio = socketio.AsyncServer(async_mode='sanic')
sio.attach(app)
fs = AFileStream("/proc/meminfo")

class AFileStream(object):
    def __init__(self, name, delay=1):
        self.name = name
        self.delay = delay

    async def read_stream(self):
        with open(self.name, "r") as current:
            current.seek(0)      # Go to the end of the file
            while True:
                 content = await self.parse(current.read().strip())
                 if not content:
                     time.sleep(self.delay)    # Sleep briefly
                     continue
                 return content

    async def parse(self, stream):
        t = time.time()
        output = { "time": t }
        lines = stream.split("\n")
        for line in lines:
            key, val = line.split(":")
            output[key.strip()] = val.strip()
        return output

    def __await__(self):
        return self.read_stream().__await__()

@app.route("/")
async def test(request):
    return json({"hello": "world"})

@app.route("/nodes")
async def test(request):
    dorm.discover()
    return json(dorm._node_store)

@app.route("/node_ids")
async def test(request):
    dorm.discover()
    return json([n._id for n in dorm._node_store])

@app.route("/models", methods=['GET', 'POST', 'OPTIONS'])
async def test(request):
    ad = request.json
    nid=None
    if ad:
        nid = ad['node_id']
    node = None
    for n in dorm._node_store:
        if n.id == nid:
            print(n)
            node = n
    if nid and node:
        return json(node.collect_models())
    else:
        return json([])

@app.route("/node", methods=['GET', 'POST'])
async def test(request):
    return json(dorm._node_store[0]._id)

@app.route("/create_node/", methods=['GET'])
async def test(request):
    n = dorm.create_node()

    return json({ "parsed": True, "body": vars(n)})

@sio.on('ping_from_client')
async def ping(sid):
    data = await fs
    await sio.emit('pong_from_server', data, room=sid)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=1307, debug=True)
