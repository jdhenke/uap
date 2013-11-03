# interface to uap's semantic network
# nodes are concepts from a semantic network
# links are the relatedness of two concepts
define ["core/dataProvider", "core/singleton", "core/keyListener", "core/selection", "core/graphModel", "uap/dimSlider"],
(DataProvider, Singleton, KeyListener, Selection, GraphModel, DimSlider) ->

  # minStrength is the minimum similarity
  # two nodes must have to be considered linked.
  # this is evaluated at the minimum dimensionality
  minStrength = 0.75

  class ConceptProvider extends DataProvider

    constructor: (@graphModel, @keyListener, @selection, @dimSlider) ->
      super(@graphModel, @keyListener, @selection)

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
        minStrength: minStrength
      @ajax "get_related_nodes", data, callback

    # initialize each link's strength before being added to the graph model
    linkFilter: (link) ->
      @dimSlider.setLinkStrength(link)
      return true

  class ConceptProviderAPI extends ConceptProvider
      constructor: () ->
        graphModel = GraphModel.getInstance()
        keyListener = KeyListener.getInstance()
        selection = Selection.getInstance()
        dimSlider = DimSlider.getInstance()
        super(graphModel, keyListener, selection, dimSlider)

  _.extend ConceptProviderAPI, Singleton
