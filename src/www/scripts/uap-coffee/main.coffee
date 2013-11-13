localStorage.clear()
requirejs.config

  # must point to the URL corresponding to the celestrium repo
  baseUrl: "/scripts/celestrium/core"
  # specifies namespace and URL path to my custom plugins
  paths: "uap": "../../uap/"

# main entry point
require ["Celestrium"], (Celestrium) ->

  # call with server's response to ping about dimensionality
  main = (response) ->

    # initialize the workspace with all the below plugins
    Celestrium.init
      # these come with celestrium
      # their arguments should be specific to this data set
      "Layout":
        "el": document.querySelector "#workspace"
        "title": "UAP"
      "KeyListener":
        document.querySelector "body"
      "GraphModel":
        "nodeHash": (node) -> node.text
        "linkHash": (link) -> link.source.text + link.target.text
      "GraphView": {}
      "Sliders": {}
      "ForceSliders": {}
      "NodeSearch":
        prefetch: "get_nodes"
      "Stats": {}
      "NodeSelection": {}
      "NodeDetails": {}
      "LinkDistribution": {}
      # these are plugins i defined specific to this data set
      "uap/DimSlider":
        [response.min, response.max]
      "uap/ConceptProvider": {}
      "uap/CodeLinks": {}

  # ask server for range of dimensionalities
  $.ajax
    url: "get_dimensionality_bounds"
    success: main
