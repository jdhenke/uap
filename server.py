import os, sys, cherrypy
import simplejson as json
from providers import ConceptProvider, AssertionProvider

class Server(object):

  _cp_config = {'tools.staticdir.on' : True,
                'tools.staticdir.dir' : os.path.abspath(os.path.join(os.getcwd(), "www")),
                'tools.staticdir.index' : 'index.html',
                }

  def __init__(self):
    self.provider = ConceptProvider(100)

  @cherrypy.expose
  @cherrypy.tools.json_out()
  def get_nodes(self):
    return self.provider.get_nodes();

  @cherrypy.expose
  @cherrypy.tools.json_out()
  def get_edges(self, node, otherNodes):
    return self.provider.get_edges(json.loads(node), json.loads(otherNodes))

  @cherrypy.expose
  @cherrypy.tools.json_out()
  def get_related_nodes(self, nodes, minStrength):
    return self.provider.get_related_nodes(json.loads(nodes), float(minStrength))

cherrypy.config.update({'server.socket_host': '0.0.0.0', 
                         'server.socket_port': int(sys.argv[1]), 
                        }) 

cherrypy.quickstart(Server())
