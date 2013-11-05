import math, numpy, divisi2

def create_graph(matrix, numAxesStr, graphType):
  if graphType == 'concepts':
    return ConceptGraph(matrix, numAxesStr)
  elif graphType == 'assertions':
    return AssertionGraph(matrix, numAxesStr)
  raise Exception("unrecognized graph type: [%s]" % (graphType, ))

class Graph(object):

  def get_nodes(self):
    raise NotImplementedError()

  def get_edges(self):
    raise NotImplementedError()

  def get_related_nodes(self):
    raise NotImplementedError()

class ParticularSVDGraphWrapper(object):
  def __init__(self, matrix, numAxes):
    self.concept_axes, self.axis_weights, self.feature_axes = matrix.svd(k=numAxes)
    self.predictions = divisi2.reconstruct(self.concept_axes,
                                           self.axis_weights,
                                           self.feature_axes)
    self.sim = divisi2.reconstruct_similarity(self.concept_axes,
                                              self.axis_weights,
                                              post_normalize=True)
  def get_concept_similarity(self, a, b):
    return self.sim.entry_named(a, b)

  def get_assertion_similarity(self, a1, a2):
    if a1["relation"] != a2["relation"]:
      return 0
    s1 = self.sim.entry_named(a1["concept1"], a2["concept1"])
    s2 = self.sim.entry_named(a1["concept2"], a2["concept2"])
    return 2.0 * s1 * s2 / (s1 + s2) # harmonic mean

  def get_truth(self, concept1, concept2, relation):
    try:
      return self.predictions.entry_named(concept1, ('right', relation, concept2))
      # normalize all numbers to (0,1)
      return math.atan(raw_truth)/math.pi + 0.5
    except:
      return 0

  def get_related_concepts(self, a, n):
    return self.sim.row_named(a).top_items(n=n)

class KBGraph(Graph):

  def __init__(self, matrix, axesCounts):
    self.matrix = matrix
    self.graphs = {}
    for numAxes in axesCounts:
      self.graphs[numAxes] = ParticularSVDGraphWrapper(matrix, numAxes)

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
    return list(self.matrix.row_labels)

  def get_edges(self, concept, otherConcepts):
    output = []
    for otherConcept in otherConcepts:
      a, b = concept["text"], otherConcept["text"]
      output.append(self.get_concept_similarity_coeffs(a, b))
    return output

  def get_related_nodes(self, concepts, minStrength):
    newConceptsSet = set()
    subGraph = self.graphs[self.get_dimensionality_bounds()["min"]]
    for concept in concepts:
      limit = 50
      relatedConcepts = subGraph.sim.row_named(concept["text"]).top_items(n=limit)
      i = 0
      while i < len(relatedConcepts) and relatedConcepts[i][1] > minStrength:
        relatedConcept, strength = relatedConcepts[i]
        newConceptsSet.add(relatedConcept)
        i += 1
    return [{"text": concept} for concept in newConceptsSet]

class AssertionGraph(KBGraph):

  def get_concepts(self):
    return list(self.matrix.row_labels)

  def get_relations(self):
    return ["AtLocation",
            "CapableOf",
            "ConceptuallyRelatedTo",
            "CreatedBy",
            "Causes",
            "CausesDesire",
            "DefinedAs",
            "Desires",
            "HasA",
            "HasProperty",
            "HasSubevent",
            "HasFirstSubevent",
            "HasLastSubevent",
            "HasPrerequisite",
            "IsA",
            "InheritsFrom",
            "LocatedNear",
            "MadeOf",
            "MotivatedByGoal",
            "ObstructedBy",
            "PartOf",
            "ReceivesAction",
            "SymbolOf",
            "UsedFor"]

  def get_edges(self, assertion, otherAssertions):
    output = []
    for a in otherAssertions:
      output.append(self.get_assertion_similarity_coeffs(a, assertion))
    return output

  def get_related_nodes(self, assertions, minRelatedness):
    output = {}
    subGraph = self.graphs[self.get_dimensionality_bounds()["max"]]
    for assertion in assertions:
      relation = assertion["relation"]
      c1 = assertion["concept1"]
      c2 = assertion["concept2"]
      related1 = subGraph.get_related_concepts(c1, 100)
      related2 = subGraph.get_related_concepts(c2, 100)
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
          if relatedness > minRelatedness and newAssertion["truth_coeffs"] != [0,0,0,0]:
            output[text] = (newAssertion["truth_coeffs"][-1], newAssertion)
    return [x[1] for x in sorted(output.values())[-25:]]

  def get_truth(self, concept1, concept2, relation):
    truth_coeffs = self.get_truth_coeffs(concept1, concept2, relation)
    return {"truth_coeffs": truth_coeffs}
