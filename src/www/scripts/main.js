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

  function main(response) {

    var dimModel = new Backbone.Model({});
    dimModel.set("minDimensionality", response.min);
    dimModel.set("maxDimensionality", response.max);
    dimModel.set("dimensionality", response.max);

    function setLinkStrength(link) {
      var coeffs = link.coeffs;
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
      link.strength = Math.min(1, Math.max(0, strength));
    }

    var dataProvider = new function() {
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
          minStrength: 0.75,
        };
        this.ajax('get_related_nodes', data, callback);
      };

      this.ajax = function(url, data, callback) {
        $.ajax({
          url: url,
          data: data,
          success: callback,
        });
      };

      this.filter = function(link) {
        setLinkStrength(link);
        return link.strength > 0.1;
      };
    };

    var workspace = Celestrium.createWorkspace({
      el: document.querySelector("#workspace"),
      dataProvider: dataProvider,
      nodePrefetch: "get_nodes",
      nodeAttributes: {
        conceptText: {
          type: "nominal",
          getValue: function(node) {
            return node.text;
          },
        },
      },
    });

    workspace.graphModel.on("add:link", function(link) {
      setLinkStrength(link);
      dimModel.on("change:dimensionality", function() {
        setLinkStrength(link);
      });
    });
    dimModel.on("change:dimensionality", function() {
      workspace.graphModel.trigger("change:links");
      workspace.graphModel.trigger("change");
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
  }

  $.ajax({
    url: "get_dimensionality_bounds",
    success: main,
  });

});
