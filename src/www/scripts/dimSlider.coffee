define ["core/singleton", "core/graphModel", "core/workspace"],
(Singleton, GraphModel, Workspace) ->

  class DimSliderView extends Backbone.View

    constructor: (@minDimensionality, @maxDimensionality, @graphModel) ->

      # create internal state to maintain current dimensionality
      @dimModel = new Backbone.Model({})
      @dimModel.set "minDimensionality", @minDimensionality
      @dimModel.set "maxDimensionality", @maxDimensionality
      @dimModel.set "dimensionality", @maxDimensionality

      # update link strengths when the dimensionality changes
      @listenTo @dimModel, "change:dimensionality", () ->
        # note: supplying `this` as the context is necessary
        _.each @graphModel.getLinks(), @setLinkStrength, this
        @graphModel.trigger "change:links"
        @graphModel.trigger "change"

      super()

    render: () ->

      # create scale to map dimensionality to slider value in ui
      scale = d3.scale.linear()
        .domain([@minDimensionality, @maxDimensionality])
        .range([0, 100])

      # add label to view
      $("""<span>Dimensionality: </span>""")
        .appendTo(@$el)

      # add slider to view, adjusting the underlying state as it changes
      $slider = $("<input type=\"range\" min=\"0\" max=\"100\" />")
        .val(scale(@dimModel.get("dimensionality")))
        .on "change", () =>
          @dimModel.set "dimensionality", scale.invert($slider.val())
          $slider.blur()
        .appendTo(@$el)

      # allow chained function calls
      return this

    # recompute the strength of the link based on
    # its coefficients and current dimensionality
    setLinkStrength: (link) ->
      link.strength = @reconstructPoly(link.coeffs)

    # reconstruct polynomial from coefficients
    # from least squares polynomial fit done server side,
    # and return the strength that polynomial evaluated
    # at the current dimensionality
    reconstructPoly: (coeffs) ->
      degree = coeffs.length
      strength = 0
      dimensionality = @dimModel.get("dimensionality")
      dimMultiple = 1
      i = coeffs.length
      while i > 0
        i -= 1
        strength += coeffs[i] * dimMultiple
        dimMultiple *= dimensionality
      Math.min 1, Math.max(0, strength)

  class DimSliderAPI extends DimSliderView
    constructor: (opts) ->
      [min, max] = opts
      graphModel = GraphModel.getInstance()
      super(min, max, graphModel)
      @render()
      workspace = Workspace.getInstance()
      workspace.addTopLeft @el

  _.extend DimSliderAPI, Singleton
