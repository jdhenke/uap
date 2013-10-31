import re, numpy, urllib2, divisi2
from divisi2.sparse import SparseMatrix

def get_matrix(knowledgebaseURI):
  if knowledgebaseURI == 'conceptnet':
    return create_conceptnet_matrix()
  elif knowledgebaseURI == 'tv':
    return create_tv_matrix('https://gist.github.com/jdhenke/b2c3ca72237e51426330/raw/fe383b95ea12c7a857c9924c79c326fc3f8c8d26/tv-assertions.txt')
  raise Exception('unrecognized knowledgebase URI: [%s]' % (knowledgebaseURI, ))

def create_conceptnet_matrix():
  return divisi2.network.conceptnet_matrix('en')

def create_tv_matri(path):

  USE_LEFT_ASSERTIONS = True
  relations = [u"has part", u"has property", u"capable of", u"is a", u"located at", u"used for"]

  def normalize_line(line):
    return unicode(re.sub("[^\w ]", "", line).lower())

  def get_cells(line):
    relation = get_relation(line)
    concept1, concept2 = [x.strip() for x in line.split(relation)]
    value1 = float(1)
    row1 = concept1
    col1 = ('right', relation, concept2)
    yield value1, row1, col1
    if USE_LEFT_ASSERTIONS:
      value2 = float(1)
      row2 = concept2
      col2 = ('left', relation, concept1)
      yield value2, row2, col2

  def get_relation(line):
    for relation in relations:
      if relation in line:
        return relation
    raise Exception("no known relation in line: [%s]" % line)

  values, rows, cols = [], [], []
  for raw_line in urllib2.urlopen(path):
    line = normalize_line(raw_line)
    if len(line) == 0:
      continue
    for value, row, col in get_cells(line):
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
