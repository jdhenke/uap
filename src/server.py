import os, sys, graph, cherrypy, knowledgebase
import simplejson as json

'''USAGE: python src/server.py <knowledgebase-uri> <num-axes> <concepts|assertions> <port>'''

knowledgebaseURI, numAxesStr, graphType, portStr = sys.argv[1:]

class Server(object):

  _cp_config = {'tools.staticdir.on' : True,
                'tools.staticdir.dir' : os.path.abspath(os.path.join(os.getcwd(), "src/www")),
                'tools.staticdir.index' : 'index.html',
                }

  def __init__(self, knowledgebaseURI, numAxes, graphType):
    matrix = knowledgebase.getMatrix(knowledgebaseURI)
    self.graph = graph.createGraph(matrix.svd(k=numAxes), graphType)
    if graphType == 'assertions':
      Server._cp_config['tools.staticdir.index'] = 'index-assertions.html'

  @cherrypy.expose
  @cherrypy.tools.json_out()
  def get_nodes(self):
    return self.graph.get_nodes();

  @cherrypy.expose
  @cherrypy.tools.json_out()
  def get_edges(self, node, otherNodes):
    return self.graph.get_edges(json.loads(node), json.loads(otherNodes))

  @cherrypy.expose
  @cherrypy.tools.json_out()
  def get_related_nodes(self, nodes, minStrength):
    return self.graph.get_related_nodes(json.loads(nodes), float(minStrength))

cherrypy.config.update({'server.socket_host': '0.0.0.0',
                        'server.socket_port': int(portStr),
                       })

cherrypy.quickstart(Server(knowledgebaseURI, int(numAxesStr), graphType))
