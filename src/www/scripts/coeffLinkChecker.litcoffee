This is a custom link checker for my UAP proejct.
It expects a `coeffs` attribute rather than a `strength`s.

    define ["jquery"], ($) ->
      (graphModel, dataProvider) ->
        graphModel.on "add:node", (node) ->
          nodes = graphModel.getNodes()
          dataProvider.getLinks node, nodes, (links) ->
            _.each links, (coeffs, i) ->
              link =
                source: node
                target: nodes[i]
                coeffs: coeffs

              graphModel.putLink link if !dataProvider.filter? or dataProvider.filter(link)