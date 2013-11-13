from transform import createSparseMatrix

# modify me to return a list or be a generator of your assertions
def getAssertions():
  yield "joe", "in", "school"
  yield "school", "in", "ma"

createSparseMatrix(getAssertions(), "kb.pickle")
