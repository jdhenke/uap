import math, numpy, divisi2

def create_graph(matrix_path, dim_list, node_type):
  matrix = divisi2.load(matrix_path)
  if node_type == 'concepts':
    return ConceptGraph(matrix, dim_list)
  elif node_type == 'assertions':
    return AssertionGraph(matrix, dim_list)
  raise Exception("unrecognized node type: [%s]" % (node_type, ))

class KBGraph(object):

  def __init__(self, matrix, dim_list):
    self.matrix = matrix
    self.graphs = {}
    for numAxes in dim_list:
      self.graphs[numAxes] = ParticularSVDGraphWrapper(matrix, numAxes)
    self.concepts = list(self.matrix.row_labels)
    self.relations = list(set([feature[1] for feature in self.matrix.col_labels]))
    def indent(obj):
      output = []
      for line in str(obj).split("\n"):
        output.append("    " + line)
      return "\n".join(output)

  def get_dimensionality_bounds(self):
    return {"min": min(self.graphs.keys()), "max": max(self.graphs.keys())}

  def get_concept_similarity_coeffs(self, a, b):
    f = lambda graph: graph.get_concept_similarity(a, b)
    return self._get_coeffs(f)

  def get_assertion_similarity_coeffs(self, a, b):
    f = lambda graph: graph.get_assertion_similarity(a, b)
    return self._get_coeffs(f)

  def get_truth_coeffs(self, concept1, concept2, relation):
    f = lambda graph: graph.get_truth(concept1, concept2, relation)
    return self._get_coeffs(f)

  def _get_coeffs(self, f):
    x = [numAxes for numAxes, graph in self.graphs.iteritems()]
    y = [f(graph) for numAxes, graph in self.graphs.iteritems()]
    coeffs = numpy.polyfit(x, y, len(x) - 1)
    return list(coeffs)

class ConceptGraph(KBGraph):

  def get_nodes(self):
    return self.concepts

  def get_edges(self, concept, otherConcepts):
    output = []
    for otherConcept in otherConcepts:
      a, b = concept["text"], otherConcept["text"]
      output.append(self.get_concept_similarity_coeffs(a, b))
    return output

  def get_related_nodes(self, concepts, num_nodes):
    newConceptsSet = set()
    subGraph = self.graphs[self.get_dimensionality_bounds()["max"]]
    for concept in concepts:
      relatedConcepts = subGraph.get_related_concepts(concept["text"], num_nodes)
      newConceptsSet |= set([(b, a) for a,b in relatedConcepts])
    return [{"text": x[1]} for x in sorted(newConceptsSet, reverse=True)[:num_nodes]]

class AssertionGraph(KBGraph):

  def get_concepts(self):
    return self.concepts

  def get_relations(self):
    return self.relations

  def get_edges(self, assertion, other_assertions):
    output = []
    for a in other_assertions:
      output.append(self.get_assertion_similarity_coeffs(a, assertion))
    return output

  def get_related_nodes(self, assertions, num_nodes):
    output = {}
    subGraph = self.graphs[self.get_dimensionality_bounds()["max"]]
    for assertion in assertions:
      relation = assertion["relation"]
      c1 = assertion["concept1"]
      c2 = assertion["concept2"]
      related1 = subGraph.get_related_concepts(c1, 20)
      related2 = subGraph.get_related_concepts(c2, 20)
      for ca, relatednessA in related1:
        for cb, relatednessB in related2:
          text = "%s %s %s" % (ca, relation, cb, )
          if text in output:
            continue
          try:
            truth_coeffs = self.get_truth_coeffs(ca, cb, relation)
          except KeyError as e:
            continue
          newAssertion = {
            "concept1": ca,
            "concept2": cb,
            "relation": relation,
            "text": text,
            "truth_coeffs": truth_coeffs,
          }
          relatedness = subGraph.get_assertion_similarity(assertion, newAssertion)
          output[text] = (relatedness, newAssertion)
    return [x[1] for x in sorted(output.values(), reverse=True)[:num_nodes]]

  def get_truth(self, concept1, concept2, relation):
    truth_coeffs = self.get_truth_coeffs(concept1, concept2, relation)
    return {"truth_coeffs": truth_coeffs}

class ParticularSVDGraphWrapper(object):

  def __init__(self, matrix, dimensionality):
    concept_axes, axis_weights, feature_axes = matrix.svd(k=dimensionality)
    self.predict = divisi2.reconstruct(concept_axes,
                                       axis_weights,
                                       feature_axes)
    self.concept_sim = divisi2.reconstruct_activation(concept_axes,
                                                      axis_weights,
                                                      post_normalize=True)
    self.feature_sim = divisi2.reconstruct_activation(feature_axes,
                                                      axis_weights,
                                                      post_normalize=True)
  def get_concept_similarity(self, a, b):
    return max(0, min(1, self.concept_sim.entry_named(a, b)))

  def get_assertion_similarity(self, a1, a2):
    right_feature1 = ('right', a1["relation"], a1["concept2"])
    right_feature2 = ('right', a2["relation"], a2["concept2"])
    left_feature1 = ('left', a1["relation"], a1["concept1"])
    left_feature2 = ('left', a2["relation"], a2["concept1"])
    right_sim = self.get_feature_similarity(right_feature1, right_feature2)
    left_sim = self.get_feature_similarity(left_feature1, left_feature2)
    def harmonic_mean(s1, s2):
      if s1 + s2 == 0:
        return 0
      else:
        return 2.0 * s1 * s2 / (s1 + s2)
    return max(0, min(1, harmonic_mean(right_sim, left_sim)))

  def get_feature_similarity(self, f1, f2):
    try:
      return max(0, min(1, self.feature_sim.entry_named(f1, f2)))
    except KeyError:
      return 0

  def get_truth(self, concept1, concept2, relation):
    try:
      raw_truth = self.predict.entry_named(concept1, ('right', relation, concept2))
      # normalize all numbers to (0,1) using a sigmoid function
      return 1/(1+(math.e **(-3 * raw_truth)))
    except KeyError:
      return 0

  def get_related_concepts(self, a, n):
    return self.concept_sim.row_named(a).top_items(n=n)

  def get_related_features(self, f, n):
    return self.feature_sim.row_named(f).top_items(n=n)
