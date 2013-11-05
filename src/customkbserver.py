import sys, numpy, graph, divisi2, cherrypy
from divisi2.sparse import SparseMatrix
from server import Server

'''

Define your own get_assertions and get_relations functions
in CustomKnowledgebase.

Then run the server following the usage instructions below
and go to http://localhost:PORT on the port you specified.

'''

class CustomKnowledgebase(object):


  ### DEFINE ME ###
  def get_assertions(self):
    yield Assertion("water", "IsA", "drink")

  ### DEFINE ME ###
  def get_relations(self):
    return ["IsA"]

  def to_sparse_matrix(self):
    values, rows, cols = [], [], []
    for assertion in self.get_assertions():
      for value, row, col in assertion.get_cells():
        values.append(value)
        rows.append(row)
        cols.append(col)
    row_labels = set(rows)
    col_labels = set(cols)
    sparseMatrix = SparseMatrix((len(row_labels), len(col_labels)), row_labels=row_labels, col_labels=col_labels)
    assert len(values) == len(rows) and len(rows) == len(cols)
    for i in xrange(len(values)):
      value, row, col = values[i], rows[i], cols[i]
      sparseMatrix.set_entry_named(row, col, value)
    return sparseMatrix

class Assertion(object):
  def __init__(self, concept1, relation, concept2):
    self.concept1 = concept1
    self.relation = relation
    self.concept2 = concept2
  def get_cells(self):
    value1 = float(1)
    row1 = self.concept1
    col1 = ('right', self.relation, self.concept2)
    yield value1, row1, col1
    if True: # USE LEFT ASSERTIONS?
      value2 = float(1)
      row2 = self.concept2
      col2 = ('left', self.relation, self.concept1)
      yield value2, row2, col2

class CustomServer(Server):
  def __init__(self, kb, axesArray, nodeType):
    self.kb = kb
    matrix = kb.to_sparse_matrix()
    self.graph = graph.create_graph(matrix, axesArray, nodeType)
    if nodeType == 'assertions':
      Server._cp_config['tools.staticdir.index'] = 'index-assertions.html'
    else:
      assert nodeType == "concepts", "invalid nodeType: %s" %\
        (nodeType, )

  @cherrypy.expose
  @cherrypy.tools.json_out()
  def get_relations(self):
    return self.kb.get_relations()

if __name__ == '__main__':
  try:

    # parse and validate command line arguments
    assert len(sys.argv) == 4, "incorrect number of arguments"
    axesString, nodeType, portStr = sys.argv[1:4]
    axesArray = [int(x) for x in axesString.split(",")]
    for x in axesArray: assert x > 0, "axes count %s is not positive" %\
      (x, )
    assert len(axesArray) == len(set(axesArray)),\
      "same axes count specified more than once"
    nodeType = nodeType.lower()
    assert nodeType in {"concepts", "assertions"},\
      "invalid node type: %s" % (nodeType, )

    # create assertion provider
    kb = CustomKnowledgebase()

    # create and run server
    cherrypy.config.update({'server.socket_host': '0.0.0.0',
                            'server.socket_port': int(portStr),
                           })
    cherrypy.quickstart(CustomServer(kb, axesArray, nodeType))

  except AssertionError as e:
    print "Exception encountered: %s" % (e, )
    print """
Command line usage:

  python customkbserver.py AXES-STRING NODE-TYPE PORT

    AXES-STRING ::= comma separated distinct, positive integers which are
                    each a number of axes the inference will be
                    performed at.

    NODE-TYPE ::= either "concepts" or "assertions"
                  specifies what nodes are to be considered in the graph

    PORT ::= valid port on which to run the server

Examples:

    python customkbserver.py 100 concepts 5000

    python src/customkbserver.py 5,10,50,100 assertions 8080

    """
