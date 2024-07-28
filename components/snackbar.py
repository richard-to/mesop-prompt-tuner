from typing import Callable, Literal

import mesop as me


@me.component
def snackbar(
  *,
  is_visible: bool,
  label: str,
  action_label: str | None = None,
  on_click_action: Callable | None = None,
  horizontal_position: Literal["start", "center", "end"] = "center",
  vertical_position: Literal["start", "center", "end"] = "end",
):
  """Creates a snackbar.

  By default the snackbar is rendered at bottom center.

  The on_click_action should typically close the snackbar as part of its actions. If no
  click event is included, you'll need to manually hide the snackbar.

  Note that there is one issue with this snackbar example. No actions are possible until
  the snackbar is dismissed or closed. This is due to the fixed box that gets created when
  the snackbar is visible.

  Args:
    is_visible: Whether the snackbar is currently visible or not.
    label: Message for the snackbar
    action_label: Optional message for the action of the snackbar
    on_click_action: Optional click event when action is triggered.
    horizontal_position: Horizontal position of the snackbar
    vertical_position: Vertical position of the snackbar
  """
  with me.box(
    style=me.Style(
      display="block" if is_visible else "none",
      height="100%",
      overflow_x="auto",
      overflow_y="auto",
      position="fixed",
      width="100%",
      z_index=1000,
    )
  ):
    with me.box(
      style=me.Style(
        align_items=vertical_position,
        height="100%",
        display="flex",
        justify_content=horizontal_position,
      )
    ):
      with me.box(
        style=me.Style(
          align_items="center",
          background="#2f3033",
          border_radius=5,
          box_shadow=("0 3px 1px -2px #0003, 0 2px 2px #00000024, 0 1px 5px #0000001f"),
          display="flex",
          font_size=14,
          justify_content="space-between",
          margin=me.Margin.all(10),
          padding=me.Padding(top=5, bottom=5, right=5, left=15)
          if action_label
          else me.Padding.all(15),
          width=300,
        )
      ):
        me.text(label, style=me.Style(color="#fcfcfc"))
        if action_label:
          me.button(
            action_label,
            on_click=on_click_action,
            style=me.Style(color="#d6e3fe"),
          )
