from typing import Callable, Literal, Any

import mesop as me

from components import helpers


@me.component()
def button(
  label: str | None = None,
  *,
  on_click: Callable[[me.ClickEvent], Any] | None = None,
  type: Literal["raised", "flat", "stroked"] | None = None,
  color: Literal["primary", "accent", "warn"] | None = None,
  disable_ripple: bool = False,
  disabled: bool = False,
  style: me.Style | None = None,
  key: str | None = None,
) -> None:
  me.button(
    label=label,
    on_click=on_click,
    type=type,
    color=color,
    disable_ripple=disable_ripple,
    disabled=disabled,
    key=key,
    style=helpers.merge_styles(me.Style(border_radius=10), style),
  )


@me.component()
def button_toggle(
  labels: list[str],
  selected: str = "",
  on_click: Callable | None = None,
  key: str = "",
):
  """Simple version of Angular Component Button toggle.

  Only supports single selection for now.

  Args:
    labels: Text labels for buttons
    selected: Selected label
    on_click: Event to handle button clicks on the button toggle
    key: The key will be used as as prefix along with the selected label
  """
  with me.box(style=me.Style(display="flex", font_weight="bold", font_size=14)):
    last_index = len(labels) - 1

    for index, label in enumerate(labels):
      if index == 0:
        element = "first"
      elif index == last_index:
        element = "last"
      else:
        element = "default"

      with me.box(
        key=key + "_" + label,
        on_click=on_click,
        style=me.Style(
          align_items="center",
          display="flex",
          # Handle selected case
          background=_SELECTED_BG
          if label == selected
          else me.theme_var("surface-container-lowest"),
          padding=_SELECTED_PADDING if label == selected else _PADDING,
          cursor="default" if label == selected else "pointer",
          # Handle single button case (should just use a button in this case)
          border=_LAST_BORDER if last_index == 0 else _BORDER_MAP[element],
          border_radius=_BORDER_RADIUS if last_index == 0 else _BORDER_RADIUS_MAP[element],
        ),
      ):
        if label in selected:
          me.icon("check")
        me.text(label)


_SELECTED_BG = me.theme_var("primary-container")

_PADDING = me.Padding(left=15, right=15, top=10, bottom=10)
_SELECTED_PADDING = me.Padding(left=15, right=15, top=5, bottom=5)

_BORDER_RADIUS = "20px"

_DEFAULT_BORDER_STYLE = me.BorderSide(width=1, color=me.theme_var("outline"), style="solid")
_BORDER = me.Border(
  left=_DEFAULT_BORDER_STYLE, top=_DEFAULT_BORDER_STYLE, bottom=_DEFAULT_BORDER_STYLE
)
_LAST_BORDER = me.Border.all(_DEFAULT_BORDER_STYLE)

_BORDER_MAP = {
  "first": _BORDER,
  "last": _LAST_BORDER,
  "default": _BORDER,
}

_BORDER_RADIUS_MAP = {
  "first": "20px 0 0 20px",
  "last": "0px 20px 20px 0",
  "default": "0",
}
