# provides search to add custom assertions
define ["core/singleton", "core/workspace", "core/graphModel", "core/graphView", "uap/dimSlider"],
(Singleton, Workspace, GraphModel, GraphView, DimSlider) ->

  class AssertionSearchView extends Backbone.View

    events:
      "click #btn-add": "addAssertion"

    initialize: (options) ->
      @options = options
      colorScale = d3.scale.linear()
        .domain([0, 1])
        .range(["red", "green"])
      update = (n) => colorScale(@options.dimSlider.interpolate(n.truth_coeffs))
      @options.graphView.on "enter:node", (nodeSelection) ->
        nodeSelection.attr "fill", update

      @options.dimSlider.dimModel.on "change:dimensionality", =>
        @options.graphView.getNodeSelection().attr "fill", update


    render: ->

      # create inputs
      container = $("<div />").addClass("assertion-search-container")
      conceptInput1 = $("<input type=\"text\" placeHolder=\"Concept 1...\" id=\"concept1\" />")
      relationInput = $("<input type=\"text\" placeHolder=\"Relation...\" id=\"relation\" />")
      conceptInput2 = $("<input type=\"text\" placeHolder=\"Concept 2...\" id=\"concept2\" />")
      inputContainer = $("<span />").append(conceptInput1).append(relationInput).append(conceptInput2)
      button = $("<button id=\"btn-add\">Add</button>")
      @$el.append container
      container.append(inputContainer).append button

      # apply typeahead to concept searches
      _.each [conceptInput1, conceptInput2], (conceptInput) =>
        conceptInput.typeahead
          prefetch: @options.conceptPrefetch
          name: "concepts"
          limit: 100

      # apply typeahead to relation searches
      relationInput.typeahead
        prefetch: @options.relationPrefetch
        name: "relations"

    addAssertion: ->
      concept1 = @$("#concept1").val()
      concept2 = @$("#concept2").val()
      relation = @$("#relation").val()
      text = concept1 + " " + relation + " " + concept2
      node =
        concept1: concept1
        concept2: concept2
        relation: relation
        text: text
      $.ajax
        url: "get_truth"
        data:
          node: JSON.stringify(node)
        success: (response) =>
          newNode = _.extend(node, response)
          @options.graphModel.putNode newNode

  class AssertionSearchAPI extends AssertionSearchView
    constructor: () ->
      graphModel = GraphModel.getInstance()
      graphView = GraphView.getInstance()
      dimSlider = DimSlider.getInstance()
      super
        graphModel: graphModel,
        graphView: graphView,
        conceptPrefetch: "/get_concepts",
        relationPrefetch: "/get_relations",
        dimSlider: dimSlider
      @render()
      workspace = Workspace.getInstance()
      workspace.addTopRight(@$el)

  _.extend AssertionSearchAPI, Singleton
