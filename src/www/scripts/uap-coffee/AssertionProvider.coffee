# interface to uap's semantic network
# nodes are concepts from a semantic network
# links are the relatedness of two concepts
define ["DataProvider"], (DataProvider) ->

  # minStrength is the minimum similarity
  # two nodes must have to be considered linked.
  # this is evaluated at the minimum dimensionality
  numNodes = 25

  class AssertionProvider extends DataProvider

    init: (instances) ->
      @dimSlider = instances["uap/DimSlider"]
      super(instances)

    getLinks: (node, nodes, callback) ->
      data =
        node: JSON.stringify(node)
        otherNodes: JSON.stringify(nodes)
      @ajax "get_edges", data, (arrayOfCoeffs) ->
        callback _.map arrayOfCoeffs, (coeffs, i) ->
          coeffs: coeffs

    getLinkedNodes: (nodes, callback) ->
      data =
        nodes: JSON.stringify(nodes)
        numNodes: numNodes
      @ajax "get_related_nodes", data, callback

    # initialize each link's strength before being added to the graph model
    linkFilter: (link) ->
      @dimSlider.setLinkStrength(link)
      return true
