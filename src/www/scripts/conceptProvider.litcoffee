## API

## Code

    define ["core/singleton"], (Singleton) ->

      class ConceptProvider
        constructor: (@filter) ->
        getLinks: (node, nodes, callback) ->
          data =
            node: JSON.stringify(node)
            otherNodes: JSON.stringify(nodes)
          @ajax "get_edges", data, callback
        getLinkedNodes: (nodes, callback) ->
          data =
            nodes: JSON.stringify(nodes)
            minStrength: 0.75
          @ajax "get_related_nodes", data, callback
        ajax: (url, data, callback) ->
          $.ajax
            url: url
            data: data
            success: callback
