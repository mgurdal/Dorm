"""
REST the DORM in here
"""
from sanic import Sanic
from sanic.response import json
from dorm.dorm import DORM
import sys
app = Sanic()
dorm = DORM()

@app.route("/")
async def test(request):
    return json({"hello": "world"})

@app.route("/create_node/", methods=['POST'])
async def test(request):
    body = request.form

    container_id = body['container_id'].pop()
    ip = body['ip'].pop()
    type_ = body['type_'].pop()
    replica = body['replica'].pop()

    n = dorm.create_node(container_id, type_=type_, replica=replica)
    return json({ "parsed": True, "body": n.__fields__})


if __name__ == "__main__":

    app.run(host="0.0.0.0", port=1307)
