from components.helpers import merge_styles

from typing import Callable

import mesop as me


@me.content_component
def card(*, title: str = "", style: me.Style | None = None, key: str = ""):
  """Creates a simple card component similar to Angular Component.

  Args:
    title: If empty, not title will be shown
    style: Override the default styles of the card box
    key: Not really useful here
  """
  with me.box(key=key, style=merge_styles(_DEFAULT_CARD_STYLE, style)):
    if title:
      me.text(
        title,
        style=me.Style(font_size=16, font_weight="bold", margin=me.Margin(bottom=15)),
      )

    me.slot()


@me.content_component
def expanable_card(
  *,
  title: str = "",
  expanded: bool = False,
  on_click_header: Callable | None = None,
  style: me.Style | None = None,
  key: str = "",
):
  """Creates a simple card component that is expandable.

  Args:
    title: If empty, no title will be shown but the expander will still be shown
    expanded: Whether the card is expanded or not
    on_click_header: Click handler for expanding card
    style: Override the default styles of the card box
    key: Key for the component
  """
  with me.box(key=key, style=merge_styles(_DEFAULT_CARD_STYLE, style)):
    with me.box(
      on_click=on_click_header,
      style=me.Style(
        align_items="center",
        display="flex",
        justify_content="space-between",
      ),
    ):
      me.text(
        title,
        style=me.Style(font_size=16, font_weight="bold"),
      )
      me.icon("keyboard_arrow_up" if expanded else "keyboard_arrow_down")

    with me.box(style=me.Style(margin=me.Margin(top=15), display="block" if expanded else "none")):
      me.slot()


_DEFAULT_CARD_STYLE = me.Style(
  background="#FFF",
  border_radius=10,
  border=me.Border.all(me.BorderSide(width=1, color="#DEE2E6", style="solid")),
  padding=me.Padding.all(15),
  margin=me.Margin(bottom=15),
)
