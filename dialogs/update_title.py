import mesop as me

import components as mex
import handlers
from constants import DIALOG_INPUT_WIDTH
from state import State


@me.component
def update_title():
  state = me.state(State)
  # Update prompt title dialog
  with mex.dialog(state.dialog_show_title):
    me.text("Update Prompt Title", type="headline-6")
    me.input(
      label="Title",
      value=state.temp_title,
      on_blur=handlers.on_update_input,
      key="temp_title",
      style=me.Style(width=DIALOG_INPUT_WIDTH),
    )
    with mex.dialog_actions():
      me.button("Cancel", on_click=handlers.on_close_dialog, key="dialog_show_title")
      me.button("Save", type="flat", disabled=not state.temp_title.strip(), on_click=on_save_title)


def on_save_title(e: me.InputBlurEvent):
  """Saves the title and closes the dialog."""
  state = me.state(State)
  if state.temp_title:
    state.title = state.temp_title
    state.dialog_show_title = False
