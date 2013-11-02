## Docs

Main entry point into the celestrium app via requirejs.

## Code

    requirejs.config

point to the URL corresponding to the celestrium repo

      baseUrl: "/scripts/celestrium/"

      paths:
        "uap": "../"

    # main entry point
    requirejs ["core/celestrium"], (Celestrium) ->


      plugins =

specify which celestrium features to use

        "core/workspace":
          "el": document.querySelector "#workspace"
        "core/keyListener":
          document.querySelector "body"
        "core/graphModel":
          "nodeHash": (node) -> node.text
          "linkHash": (link) -> link.source.text + link.target.text
        "core/graphView": {}
        "core/forceSliders": {}
        "core/nodeSearch":
          "get_nodes"
        "core/graphStats": {}
        "core/selection": {}
        "core/nodeProfile": {}
        "core/linkHistogram": {}

Create an interface to the backend.
This should probably get pushed back into celestrium somehow.

initialize plugins and execute the callback when done.
the plugin instances are available to this callback.

      Celestrium.init plugins, () ->
        require ["core/graphModel", "core/keyListener", "core/selection"],
        (GraphModel, KeyListener, Selection) ->

### PUSH AS MUCH AS POSSIBLE BACK INTO CELESTRIUM

          require ["uap/conceptProvider", "uap/coeffLinkChecker", "core/workspace"],
          (ConceptProvider, CoeffLinkChecker, Workspace) ->

            main = (response) ->

              graphModel = GraphModel.getInstance()

              dataProvider = new ConceptProvider (link) ->
                setLinkStrength link
                link.strength > 0.1
              linkChecker = new CoeffLinkChecker(graphModel, dataProvider)

              keyListener = KeyListener.getInstance()
              selection = Selection.getInstance()
              keyListener.on "down:16:187", ->
                dataProvider.getLinkedNodes selection.getSelectedNodes(), (nodes) =>
                  _.each nodes, (node) ->
                    graphModel.putNode node

              dimModel = new Backbone.Model({})
              dimModel.set "minDimensionality", response.min
              dimModel.set "maxDimensionality", response.max
              dimModel.set "dimensionality", response.max

              setLinkStrength = (link) ->
                link.strength = interpolate(link.coeffs)
              interpolate = (coeffs) ->
                degree = coeffs.length
                strength = 0
                dimensionality = dimModel.get("dimensionality")
                dimMultiple = 1
                i = coeffs.length
                while i > 0
                  i -= 1
                  strength += coeffs[i] * dimMultiple
                  dimMultiple *= dimensionality
                Math.min 1, Math.max(0, strength)

              graphModel.on "add:link", (link) ->
                setLinkStrength link
                dimModel.on "change:dimensionality", ->
                  setLinkStrength link

              dimModel.on "change:dimensionality", ->
                graphModel.trigger "change:links"
                graphModel.trigger "change"

              scale = d3.scale.linear().domain([response.min, response.max]).range([0, 100])
              dimensionalitySliderContainer = $("<div />")
              dimensionalitySliderContainer.append $("<span />").text("Dimensionality: ")
              slider = $("<input type=\"range\" min=\"0\" max=\"100\" />").val(scale(dimModel.get("dimensionality"))).on("change", ->
                dimModel.set "dimensionality", scale.invert($(this).val())
              ).appendTo(dimensionalitySliderContainer)

              workspace = Workspace.getInstance()
              workspace.addTopLeft dimensionalitySliderContainer

            $.ajax
              url: "get_dimensionality_bounds"
              success: main
