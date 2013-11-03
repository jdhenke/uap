requirejs.config

  # must point to the URL corresponding to the celestrium repo
  baseUrl: "/scripts/celestrium/"
  # specifies namespace and URL path to my custom plugins
  paths: "uap": "../"

# main entry point
require ["core/celestrium"], (Celestrium) ->

  # call with server's response to ping about dimensionality
  main = (response) ->

    # initialize the workspace with all the below plugins
    Celestrium.init
      # these come with celestrium
      # their arguments should be specific to this data set
      "core/workspace":
        "el": document.querySelector "#workspace"
        "title": "UAP"
      "core/keyListener":
        document.querySelector "body"
      "core/graphModel":
        "nodeHash": (node) -> node.text
        "linkHash": (link) -> link.source.text + link.target.text
      "core/graphView": {}
      "core/sliders": {}
      "core/forceSliders": {}
      "core/nodeSearch":
        "get_nodes"
      "core/stats": {}
      "core/selection": {}
      "core/nodeProfile": {}
      "core/linkDistribution": {}
      # these are plugins i defined specific to this data set
      "uap/dimSlider":
        [response.min, response.max]
      "uap/conceptProvider": {}
      "uap/codeLinks": {}

  # ask server for range of dimensionalities
  $.ajax
    url: "get_dimensionality_bounds"
    success: main
