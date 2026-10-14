from api import app
import cherrypy

cherrypy.tree.graft(app, '/')
cherrypy.config.update({
  'server.socket_host': '0.0.0.0',
  'server.socket_port': 7777,
  'server.thread_pool': 20,
  'server.thread_pool_max': -1  # Set to -1 for non-blocking connections
})
cherrypy.engine.start()
cherrypy.engine.block()

#test push
# test2
