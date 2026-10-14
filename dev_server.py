from gevent import monkey
# from gevent.server import StreamServer
# from gevent.pool import Pool
monkey.patch_all()

from bottle import run
from api import app

from bottle.ext.websocket import GeventWebSocketServer

run(app, server = GeventWebSocketServer, host = '0.0.0.0', port = 8888)
