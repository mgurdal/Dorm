#!/usr/bin/env python

import asyncio
import websockets
#
async def hello():
    async with websockets.connect('ws://0.0.0.0:1307/feed') as websocket:

        greeting = await websocket.recv()
        print(greeting)

asyncio.get_event_loop().run_until_complete(hello())

# from dorm.system_utils import FileStream
#
# def coro_from_gen(generator):
#     """turn a normal generator into a coroutine that can recieve and return computed data"""
#     def input_pipe():
#         """small internal coroutine that recieves data"""
#         x = ''
#         while True:
#             x = yield x
#             yield  # to keep the generator in lock step with input
#     pipe = input_pipe()
#     next(pipe)  # prime the input coroutune
#     gen = generator(pipe)
#     n = yield  # get first item
#     while True:
#         pipe.send(n)
#         n = yield next(gen)
