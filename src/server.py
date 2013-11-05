import os, sys, graph, cherrypy, knowledgebase
import simplejson as json

'''USAGE: python src/server.py <knowledgebase-uri> <num-axes> <concepts|assertions> <port>'''

class Server(object):

  _cp_config = {'tools.staticdir.on' : True,
                'tools.staticdir.dir' : os.path.abspath(os.path.join(os.getcwd(), "src/www")),
                'tools.staticdir.index' : 'index.html',
                }

  def __init__(self, knowledgebaseURI, numAxes, graphType):
    matrix = knowledgebase.get_matrix(knowledgebaseURI)
    self.graph = graph.create_graph(matrix, numAxes, graphType)
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

  @cherrypy.expose
  @cherrypy.tools.json_out()
  def get_dimensionality_bounds(self):
    return self.graph.get_dimensionality_bounds()

  @cherrypy.expose
  @cherrypy.tools.json_out()
  def get_truth(self, node):
    node = json.loads(node)
    return self.graph.get_truth(node["concept1"], node["concept2"], node["relation"])

  @cherrypy.expose
  @cherrypy.tools.json_out()
  def get_concepts(self):
    return self.graph.get_concepts()

  @cherrypy.expose
  @cherrypy.tools.json_out()
  def get_relations(self):
    return self.graph.get_relations()

if __name__ == '__main__':
  knowledgebaseURI, numAxesStr, graphType, portStr = sys.argv[1:]
  cherrypy.config.update({'server.socket_host': '0.0.0.0',
                          'server.socket_port': int(portStr),
                         })

  cherrypy.quickstart(Server(knowledgebaseURI, numAxesStr, graphType))
