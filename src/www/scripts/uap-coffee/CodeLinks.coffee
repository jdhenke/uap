# includes a link to the uap github repo
define [], () ->
  class CodeLinks
    init: (instances) ->
      instances["Layout"].addBottomRight $ """
      <div>
        <a href="https://github.com/jdhenke/uap">uap repo</a>
      </div>
      """
