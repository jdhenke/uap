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
  }
});

/* main javascript for page */
requirejs(["celestrium/graphViewer"], 
function(GraphViewer) {
  new GraphViewer("#workspace").init();
});