/* configure requirejs dependencies */
requirejs.config({
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

/* main javascript for page */
requirejs(["jquery", "celestrium/graphModel", "celestrium/graphView", "celestrium/nodeSearch", "celestrium/selection", "celestrium/graphStats", "celestrium/forceSliders", "celestrium/linkChecker", "celestrium/keyListener", "celestrium/linkHistogram"], 
function($, GraphModel, GraphView, NodeSearch, Selection, GraphStatsView, ForceSlidersView, LinkChecker, KeyListener, LinkHistogramView) {

  var graphModel = new GraphModel({
    nodeHash: function(node) {
      return node.text;
    },
    linkHash: function(link) {
      return link.source.text + link.target.text;
    },
  });

  var graphView = new GraphView({
    model: graphModel,
  }).render();

  var dataProvider = new function() {

    var minThreshold = this.minThreshold = 0.75;
    var threshold = 0.95;

     function toJSONList(nodes) {
      return JSON.stringify(_.map(nodes, function(node) {
        return node.text;
      }));
    }

    this.getNodesPath = function() {
      return "/get_nodes";
    };

    this.addLinks = function(node) {
      var nodes = graphModel.getNodes();
      var data = {
        text: node.text,
        allNodes: toJSONList(graphModel.getNodes()),
      }
      $.ajax({
        url: "get_edges",
        data: data,
        success: function(response) {
          _.each(response, function(strength, i) {
            var link = {source:node, target: nodes[i], strength: strength};
            if (link.strength > threshold) {
              graphModel.putLink(link);
            }
          });
        }.bind(this),
      });
    }

    this.addRelatedNodes = function() {

      var data = {
        selectedNodes: toJSONList(sel.getSelectedNodes()),
        allNodes: toJSONList(graphModel.getNodes()),
        minStrength: this.minThreshold,
      };
      $.ajax({
        url: "get_related_nodes",
        data: data,
        success: function(response) {
          _.each(response.nodes, function(nodeText) {
            graphModel.putNode({text: nodeText});
          });
        },
      });
    };

  };

  new LinkChecker(graphModel, dataProvider);
  var sel = new Selection(graphModel, graphView);
  var keyListener = new KeyListener(document.querySelector("body"));

  // CTRL + A
  keyListener.on("down:17:65", sel.selectAll, sel);
  // ESC
  keyListener.on("down:27", sel.deselectAll, sel);

  // DEL
  keyListener.on("down:46", sel.removeSelection, sel);
  // ENTER
  keyListener.on("down:13", sel.removeSelectionCompliment, sel);

  // PLUS
  keyListener.on("down:16:187", dataProvider.addRelatedNodes, dataProvider);

  // / 
  keyListener.on("down:191", function(e) {
    $(".node-search-input").focus();
    e.preventDefault();
  });

  var nodeSearch = new NodeSearch({
    dataProvider: dataProvider,
    graphModel: graphModel,
  }).render();

  var graphStatsView = new GraphStatsView({
    model: graphModel,
  }).render();

  var forceSlidersView = new ForceSlidersView({
    graphView: graphView,
  }).render();

  var linkHistogramView = new LinkHistogramView({
    model: graphModel,
  }).render();

  $("#workspace").append(graphView.el);
  $("#top-left-container")
    .append(forceSlidersView.el)
    .append(linkHistogramView.el);
  $("#top-right-container").append(nodeSearch.el);
  $("#bottom-left-container").append(graphStatsView.el);

});