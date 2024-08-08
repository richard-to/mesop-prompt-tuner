import mesop as me

from web_components import markedjs_component
from web_components import copy_to_clipboard_component


@me.component
def markdown(text: str, has_copy_to_clipboard: bool = False):
  with me.box(style=me.Style(position="relative")):
    if has_copy_to_clipboard:
      with me.box(style=me.Style(position="absolute", right=0)):
        with copy_to_clipboard_component(text=text):
          with me.content_button(
            type="icon",
            style=me.Style(cursor="pointer", background=me.theme_var("surface-container")),
          ):
            me.icon("content_copy")
    markedjs_component(text)
