from gevent import monkey
# from gevent.server import StreamServer
# from gevent.pool import Pool
monkey.patch_all()

from bottle import run
from api import app

from bottle.ext.websocket import GeventWebSocketServer

run(app, server = GeventWebSocketServer, host = '0.0.0.0', port = 7777)



# def handle(socket, addr):
#     socket.sendall(b'Hello, world!\n')
#     socket.close()

# pool = Pool(10000)
# server = StreamServer(('0.0.0.0', 7777), handle, spawn = pool)
# server.serve_forever()