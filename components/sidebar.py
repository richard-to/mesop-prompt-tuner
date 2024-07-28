from typing import Callable

import mesop as me


@me.content_component
def icon_sidebar():
  """Creates a sidebar that contains icon menu items.

  Technically, does not have to be relegated to just icons menu items, but leaving it
  more specific for now.
  """
  with me.box(
    style=me.Style(
      background="#F5F8FC",
      border=me.Border.symmetric(horizontal=me.BorderSide(width=1, style="solid", color="#DEE2E6")),
      height="100%",
    )
  ):
    me.slot()


@me.component
def icon_menu_item(*, icon: str, tooltip: str, on_click: Callable | None = None, key: str = ""):
  """Creates a menu item that displays as an icon.

  - Unfortunately, we can't add a hover style
  - TODO: Add a way to determine the active menu item selected
  """
  with me.box(
    key=key,
    on_click=on_click,
    style=me.Style(
      border=me.Border(bottom=me.BorderSide(width=1, color="#DEE2E6", style="solid")),
      cursor="pointer",
      padding=me.Padding.all(15),
    ),
  ):
    with me.tooltip(message=tooltip):
      me.icon(icon)
