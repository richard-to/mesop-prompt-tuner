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

_DEFAULT_BORDER_STYLE = me.BorderSide(width=1, color=me.theme_var("outline"), style="solid")
