import mesop as me

import components as mex
import handlers
from constants import DIALOG_INPUT_WIDTH
from helpers import parse_variables
from state import State


@me.component
def add_comparisons():
  state = me.state(State)
  with mex.dialog(state.dialog_show_add_comparison):
    variable_names = set(parse_variables(state.prompt))
    me.text("Add Comparisons", type="headline-6")
    me.select(
      label="Select Versions",
      multiple=True,
      options=[
        me.SelectOption(label=f"v{prompt.version}", value=str(prompt.version))
        for prompt in state.prompts
        if prompt.version != state.version and set(prompt.variables) == variable_names
      ],
      style=me.Style(width=DIALOG_INPUT_WIDTH),
      on_selection_change=on_select_comparison,
    )
    with mex.dialog_actions():
      me.button(
        "Close",
        key="dialog_show_add_comparison",
        on_click=handlers.on_close_dialog,
        style=me.Style(border_radius="10"),
      )


def on_select_comparison(e: me.SelectSelectionChangeEvent):
  """Update UI to show the selected prompt version and close the dialog."""
  state = me.state(State)
  state.comparisons = list(map(int, e.values))
