define ["core/singleton", "core/graphModel", "core/sliders"],
(Singleton, GraphModel, Sliders) ->

  class DimSlider extends Backbone.Model

    constructor: (min, max, graphModel, sliders) ->

      # ensure backbone model components are initialized
      super()

      # create internal state to maintain current dimensionality
      @dimModel = new Backbone.Model({})
      @dimModel.set "min", min
      @dimModel.set "max", max
      @dimModel.set "dimensionality", max

      # update link strengths when the dimensionality changes
      @listenTo @dimModel, "change:dimensionality", () ->
        # note: supplying `this` as the context is necessary
        _.each graphModel.getLinks(), @setLinkStrength, this
        graphModel.trigger "change:links"
        graphModel.trigger "change"

      # create scale to map dimensionality to slider value in ui
      scale = d3.scale.linear()
        .domain([min, max])
        .range([0, 100])

      dimModel = @dimModel
      sliders.addSlider "Dimensionality", scale(@dimModel.get("dimensionality")), (val) ->
        dimModel.set "dimensionality", scale.invert val
        $(this).blur()

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

  class DimSliderAPI extends DimSlider
    constructor: (opts) ->
      [min, max] = opts
      graphModel = GraphModel.getInstance()
      sliders = Sliders.getInstance()
      super(min, max, graphModel, sliders)

  _.extend DimSliderAPI, Singleton
