requirejs.config({
  baseUrl: "/scripts/celestrium/",
  paths: {
    "jquery": "lib/jquery",
    "jquery.typeahead": "lib/jquery.typeahead",
    "underscore": "lib/underscore",
    "backbone": "lib/backbone",
    "d3": "lib/d3",
  },
  shim: {
    'jquery.typeahead': ['jquery'],
    'd3': {
      exports: "d3",
    },
    'underscore': {
      exports: '_',
    },
    'backbone': {
      deps: ['underscore'],
      exports: 'Backbone',
    },
  }
});

requirejs(["core/celestrium"], function(Celestrium) {

  var dataProvider = new function() {
    this.minThreshold = 0.94;
    this.getLinks = function(node, nodes, callback) {
      var data = {
        node: JSON.stringify(node),
        otherNodes: JSON.stringify(nodes),
      }
      this.ajax('get_edges', data, callback);
    };

    this.getLinkedNodes = function(nodes, callback) {
      var data = {
        nodes: JSON.stringify(nodes),
        minStrength: this.minThreshold,
      };
      this.ajax('get_related_nodes', data, callback);
    };

    this.ajax = function(url, data, callback) {
      $.ajax({
        url: url,
        data: data,
        success: callback,
      });
    }
  };

  var workspace = Celestrium.createWorkspace({
    el: document.querySelector("#workspace"),
    dataProvider: dataProvider,
    // nodePrefetch: "get_nodes",
    nodeAttributes: {
      assertionText: {
        type: "nominal",
        getValue: function(node) {
          return node.text;
        },
      },
    },
  });

  var colorScale = d3.scale.linear()
    .domain([0, 1])
    .range(["red", "green"]);

  workspace.graphView.on("enter:node", function(nodeSelection) {
    nodeSelection.attr("fill", function(n) {
      return colorScale(n.truth);
    });
  });

  var seed = {
    "concept1": "pizza",
    "concept2": "food",
    "relation": "IsA",
    "text": "pizza IsA food",
    "raw_truth": 0.8,
    "truth": 0.9,
  }
  workspace.graphModel.putNode(seed)

});
