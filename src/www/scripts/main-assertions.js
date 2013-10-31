requirejs.config({
  baseUrl: "/scripts/celestrium/",
  paths: {
    "jquery": "lib/jquery",
    "jquery.typeahead": "lib/jquery.typeahead",
    "underscore": "lib/underscore",
    "backbone": "lib/backbone",
    "d3": "lib/d3",
    "uap": "..",
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

requirejs(["jquery", "jquery.typeahead", "underscore", "backbone", "core/celestrium", "uap/coeffLinkChecker"], function($, typeahead, _, Backbone, Celestrium, LinkChecker) {

  function main(response) {

    var dimModel = new Backbone.Model({});
    dimModel.set("minDimensionality", response.min);
    dimModel.set("maxDimensionality", response.max);
    dimModel.set("dimensionality", response.max);

    function setLinkStrength(link) {
      link.strength = interpolate(link.coeffs);
    }

    function interpolate(coeffs) {
      var degree = coeffs.length;
      var strength = 0;
      var dimensionality = dimModel.get("dimensionality");
      var dimMultiple = 1;
      var i = coeffs.length;
      while (i > 0) {
        i -= 1
        strength += coeffs[i] * dimMultiple;
        dimMultiple *= dimensionality
      }
      return Math.min(1, Math.max(0, strength));
    }

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
      nodeAttributes: {
        assertionText: {
          type: "nominal",
          getValue: function(node) {
            return node.text;
          },
        },
      },
    });

    new LinkChecker(workspace.graphModel, dataProvider);

    workspace.graphModel.on("add:link", function(link) {
      setLinkStrength(link);
      dimModel.on("change:dimensionality", function() {
        setLinkStrength(link);
      });
    });
    dimModel.on("change:dimensionality", function() {
      workspace.graphModel.trigger("change:links");
      workspace.graphModel.trigger("change");
      workspace.graphView.getNodeSelection().attr("fill", function(n) {
        return colorScale(interpolate(n.truth_coeffs));
      });
    });

    var scale = d3.scale.linear()
      .domain([response.min, response.max])
      .range([0, 100]);
    var dimensionalitySliderContainer = $("<div />");
    dimensionalitySliderContainer.append($("<span />").text("Dimensionality: "));
    var slider = $('<input type="range" min="0" max="100" />')
      .val(scale(dimModel.get("dimensionality")))
      .on("change", function() {
        dimModel.set("dimensionality", scale.invert($(this).val()));
      }).appendTo(dimensionalitySliderContainer);
    workspace.tl.append(dimensionalitySliderContainer);

    var colorScale = d3.scale.linear()
      .domain([0, 1])
      .range(["red", "green"]);

    workspace.graphView.on("enter:node", function(nodeSelection) {
      nodeSelection.attr("fill", function(n) {
        return colorScale(interpolate(n.truth_coeffs));
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

  }

  $.ajax({
    url: "get_dimensionality_bounds",
    success: main,
  });

});
