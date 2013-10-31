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

requirejs(["jquery", "jquery.typeahead", "underscore", "backbone", "core/celestrium"], function($, typeahead, _, Backbone, Celestrium) {

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

  var AssertionSearch = Backbone.View.extend({
    events: {
      "click #btn-add": "addAssertion",
    },
    initialize: function(options) {
      this.options = options;
    },
    render: function() {
      var container = $("<div />").addClass("assertion-search-container");
      var conceptInput1 = $('<input type="text" placeHolder="Concept 1..." id="concept1" />');
      var relationInput = $('<input type="text" placeHolder="Relation..." id="relation" />');
      var conceptInput2 = $('<input type="text" placeHolder="Concept 2..." id="concept2" />');
      var inputContainer = $("<span />").append(conceptInput1)
                                       .append(relationInput)
                                       .append(conceptInput2);
      var button = $('<button id="btn-add">Add</button>');
      this.$el.append(container);
      container.append(inputContainer)
               .append(button);

      // apply typeahead to assertion search
      _.each([conceptInput1, conceptInput2], function(conceptInput) {
        conceptInput.typeahead({
          prefetch: this.options.conceptPrefetch,
          name: "concepts",
          limit: 100,
        });
      }.bind(this));

      relationInput.typeahead({
        prefetch: this.options.relationPrefetch,
        name: "relations",
      });

      return this;
    },
    addAssertion: function() {
      var concept1 = this.$("#concept1").val();
      var concept2 = this.$("#concept2").val();
      var relation = this.$("#relation").val();
      var text = concept1 + " " + relation + " " + concept2;
      var node = {
        "concept1": concept1,
        "concept2": concept2,
        "relation": relation,
        "text": text,
      };
      $.ajax({
        url: "get_truth",
        data: {node: JSON.stringify(node)},
        success: function(response) {
          var newNode = _.extend(node, response);
          workspace.graphModel.putNode(newNode);
        },
      });
    },
  });

  var assertionSearch = new AssertionSearch({
    graphModel: workspace.graphModel,
    conceptPrefetch: "/get_concepts",
    relationPrefetch: "/get_relations",
  }).render();

  workspace.tr.append(assertionSearch.el);

});
