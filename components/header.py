from components.helpers import merge_styles

import mesop as me


@me.content_component
def header(
  *,
  style: me.Style | None = None,
  is_mobile: bool = False,
  max_width: int | None = 1000,
):
  """Creates a simple header component.

  Args:
    style: Override the default styles, such as background color, etc.
    is_mobile: Use mobile layout. Arranges each section vertically.
    max_width: Sets the maximum width of the header. Use None for fluid header.
  """
  default_flex_style = _DEFAULT_MOBILE_FLEX_STYLE if is_mobile else _DEFAULT_FLEX_STYLE
  if max_width and me.viewport_size().width >= max_width:
    default_flex_style = merge_styles(
      default_flex_style,
      me.Style(width=max_width, margin=me.Margin.symmetric(horizontal="auto")),
    )

  # The style override is a bit hacky here since we apply the override styles to both
  # boxes here which could cause problems depending on what styles are added.
  with me.box(style=merge_styles(_DEFAULT_STYLE, style)):
    with me.box(style=merge_styles(default_flex_style, style)):
      me.slot()


@me.content_component
def header_section():
  """Adds a section to the header."""
  with me.box(style=me.Style(display="flex", gap=5)):
    me.slot()


_DEFAULT_STYLE = me.Style(
  background=me.theme_var("surface-container"),
  border=me.Border.symmetric(
    vertical=me.BorderSide(
      width=1,
      style="solid",
      color=me.theme_var("outline-variant"),
    )
  ),
  padding=me.Padding.all(10),
)

_DEFAULT_FLEX_STYLE = me.Style(
  align_items="center",
  display="flex",
  gap=5,
  justify_content="space-between",
)

_DEFAULT_MOBILE_FLEX_STYLE = me.Style(
  align_items="center",
  display="flex",
  flex_direction="column",
  gap=12,
  justify_content="center",
)
