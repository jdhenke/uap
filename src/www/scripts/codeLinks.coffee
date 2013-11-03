define ["core/workspace", "core/singleton"], (Workspace, Singleton) ->
  class CodeLinks
    constructor: (workspace) ->
      workspace.addBottomRight($("""<div><a href="https://github.com/jdhenke/uap">uap repo</a></div>"""))

  class CodeLinksAPI extends CodeLinks
    constructor: () ->
      workspace = Workspace.getInstance()
      super(workspace)

  _.extend CodeLinksAPI, Singleton
