define ["core/dataProvider", "core/singleton", "core/keyListener", "core/selection", "core/graphModel", "uap/dimSlider"],
(DataProvider, Singleton, KeyListener, Selection, GraphModel, DimSlider) ->

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
        minStrength: 0.75 # TODO what does this mean?
      @ajax "get_related_nodes", data, callback

    linkFilter: (link) ->
      @dimSlider.setLinkStrength(link)

  class ConceptProviderAPI extends ConceptProvider
      constructor: () ->
        graphModel = GraphModel.getInstance()
        keyListener = KeyListener.getInstance()
        selection = Selection.getInstance()
        dimSlider = DimSlider.getInstance()
        super(graphModel, keyListener, selection, dimSlider)

  _.extend ConceptProviderAPI, Singleton
