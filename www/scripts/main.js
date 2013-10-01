/* configure requirejs dependencies */
requirejs.config({
  shim: {
    'jquery.typeahead': ['jquery'],
    'd3.v3.min': {
      exports: "d3",
    },
    'underscore': {
      exports: '_',
    }
  }
});

/* main javascript for page */
requirejs(["celestrium/graphViewer"], 
function(GraphViewer) {
  new GraphViewer().init();
});