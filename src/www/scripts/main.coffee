requirejs.config

  # must point to the URL corresponding to the celestrium repo
  baseUrl: "/scripts/celestrium/"
  # specifies namespace and URL path to my custom plugins
  paths: "uap": "../"

# main entry point
require ["core/celestrium"], (Celestrium) ->

  # call with server's response to pings about dimensionality
  main = (response) ->

    # initialize the workspace with all the below plugins
    Celestrium.init
      # these come with celestrium
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
      "core/linkStrengthCDF": {}
      # these are ones i defined specific to this data set
      # you should create a dataProvider
      "uap/dimSlider":
        [response.min, response.max]
       "uap/conceptProvider": {}

  # ask server for range of dimensionalities
  $.ajax
    url: "get_dimensionality_bounds"
    success: main
