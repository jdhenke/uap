import os, sys, graph, cherrypy
import simplejson as json

'''USAGE: python src/server.py <kb-file> <num-axes> <concepts|assertions> <www-path> <port>'''

class Server(object):

  def __init__(self, matrix_path, dim_list, node_type):
    self.graph = graph.create_graph(matrix_path, dim_list, node_type)

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
  def get_related_nodes(self, nodes, numNodes):
    return self.graph.get_related_nodes(json.loads(nodes), int(numNodes))

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

  # parse command line arguments
  sm_path, dim_list_str, node_type, www_path, port_str = sys.argv[1:]
  dim_list = [int(dim_str) for dim_str in dim_list_str.split(",")]
  port = int(port_str)

  # configure cherrypy to properly accept requests
  cherrypy.config.update({'server.socket_host': '0.0.0.0',
                          'server.socket_port': port})
  Server._cp_config = {
    'tools.staticdir.on' : True,
    'tools.staticdir.dir' : os.path.abspath(www_path),
    'tools.staticdir.index' :\
      'index.html' if node_type == 'concepts' else 'index-assertions.html',
  }

  # start server
  cherrypy.quickstart(Server(sm_path, dim_list, node_type))
