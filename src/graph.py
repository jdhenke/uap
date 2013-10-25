import math, divisi2

def createGraph(svd, graphType):
  if graphType == 'concepts':
    return ConceptGraph(svd)
  elif graphType == 'assertions':
    return AssertionGraph(svd)
  raise Exception("unrecognized graph type: [%s]" % (graphType, ))

class Graph(object):

  def get_nodes(self):
    raise NotImplementedError()

  def get_edges(self):
    raise NotImplementedError()

  def get_related_nodes(self):
    raise NotImplementedError()

class KBGraph(Graph):

  def __init__(self, svd):
    self.concept_axes, self.axis_weights, self.feature_axes = svd
    self.predictions = divisi2.reconstruct(self.concept_axes,
                                           self.axis_weights,
                                           self.feature_axes)
    self.sim = divisi2.reconstruct_similarity(self.concept_axes,
                                              self.axis_weights,
                                              post_normalize=True)

class ConceptGraph(KBGraph):

  def get_nodes(self):
    return [x for x in self.concept_axes.row_labels]

  def get_edges(self, concept, otherConcepts):
    return [self.sim.entry_named(concept["text"], c2["text"]) for c2 in otherConcepts]

  def get_related_nodes(self, concepts, minStrength):
    newConceptsSet = set()
    for concept in concepts:
      limit = 100
      relatedConcepts = self.sim.row_named(concept["text"]).top_items(n=limit)
      i = 0
      while i < len(relatedConcepts) and relatedConcepts[i][1] > minStrength:
        relatedConcept, strength = relatedConcepts[i]
        newConceptsSet.add(relatedConcept)
        i += 1
    return [{"text": concept} for concept in newConceptsSet]

class AssertionGraph(KBGraph):

  def get_edges(self, assertion, otherAssertions):
    output = []
    for a in otherAssertions:
      output.append(self.get_assertion_similarity(a, assertion))
    return output

  def get_related_nodes(self, assertions, minRelatedness):
    output = {}
    for assertion in assertions:
      relation = assertion["relation"]
      c1 = assertion["concept1"]
      c2 = assertion["concept2"]
      related1 = self.sim.row_named(c1).top_items(n=10)
      related2 = self.sim.row_named(c2).top_items(n=10)
      for ca, relatednessA in related1:
        for cb, relatednessB in related2:
          text = "%s %s %s" % (ca, relation, cb, )
          if text in output:
            continue
          try:
            raw_truth = self.predictions.entry_named(ca, ('right', relation, cb))
          except KeyError as e:
            continue
          # normalize, mapping all real numbers to (0,1)
          normalized_truth = math.atan(raw_truth)/math.pi + 0.5
          newAssertion = {
            "concept1": ca,
            "concept2": cb,
            "relation": relation,
            "text": text,
            "raw_truth": raw_truth,
            "truth": normalized_truth,
          }
          relatedness = self.get_assertion_similarity(assertion, newAssertion)
          if relatedness > minRelatedness:
            output[text] = newAssertion
    return output.values()

  def get_assertion_similarity(self, a1, a2):
    if a1["relation"] != a2["relation"]:
      return 0
    s1 = self.sim.entry_named(a1["concept1"], a2["concept1"])
    s2 = self.sim.entry_named(a1["concept2"], a2["concept2"])
    return 2.0 * s1 * s2 / (s1 + s2) # harmonic mean
