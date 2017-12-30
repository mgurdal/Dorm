"""
REST the DORM in here
"""
import sys
from sanic import Sanic
from sanic.response import json
from dorm.dorm import DORM
from sanic_cors import CORS, cross_origin

app = Sanic()
CORS(app)
dorm = DORM()

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
    print()
    # data = J.loads(.decode())
    ad = request.json
    print(ad)
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
    print(request.body)
    # dorm.discover()
    return json(dorm._node_store[0]._id)

@app.route("/create_node/", methods=['GET'])
async def test(request):
    # body = request.form
    #
    # container_id = body['container_id'].pop()
    # ip = body['ip'].pop()
    # type_ = body['type_'].pop()
    # replica = body['replica'].pop()

    n = dorm.create_node()

    return json({ "parsed": True, "body": vars(n)})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=1307, debug=True)
