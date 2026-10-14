from api import app

from bottle import run

run(app, host = '0.0.0.0', port = 7777, server = 'tornado')
