import divisi2
from divisi2.sparse import SparseMatrix

def createSparseMatrix(assertions, path, use_left_features = True):

  def _get_matrix_cells(assertion):
    concept1, relation, concept2 = assertion
    value1 = float(1)
    row1 = concept1
    col1 = ('right', relation, concept2)
    yield value1, row1, col1
    if use_left_features:
      value2 = float(1)
      row2 = concept2
      col2 = ('left', relation, concept1)
      yield value2, row2, col2

  values, rows, cols = [], [], []
  for assertion in assertions:
    for value, row, col in _get_matrix_cells(assertion):
      values.append(value)
      rows.append(row)
      cols.append(col)
  row_labels = set(rows)
  col_labels = set(cols)
  sparseMatrix = SparseMatrix((len(row_labels), len(col_labels)), row_labels=row_labels, col_labels=col_labels)
  assert len(values) == len(rows) and len(rows) == len(cols)
  for i in xrange(len(values)):
    value, row, col = values[i], rows[i], cols[i]
    # TODO: more explicit handling of multiple entries for same cell
    sparseMatrix.set_entry_named(row, col, value)
  divisi2.save(sparseMatrix, path)
