# provides search to add custom assertions
define [], () ->

  class AssertionSearchView extends Backbone.View

    events:
      "click #btn-add": "addAssertion"

    constructor: (@options) ->
      super()

    init: (instances) ->
      colorScale = d3.scale.linear()
        .domain([0, 1])
        .range(["red", "green"])
      update = (n) => colorScale(instances["uap/DimSlider"].interpolate(n.truth_coeffs))
      instances["GraphView"].on "enter:node", (nodeSelection) ->
        nodeSelection.attr "fill", update

      instances["uap/DimSlider"].dimModel.on "change:dimensionality", =>
        instances["GraphView"].getNodeSelection().attr "fill", update

      @render()
      instances["Layout"].addTopRight @el

      @graphModel = instances["GraphModel"]

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
          @graphModel.putNode newNode
