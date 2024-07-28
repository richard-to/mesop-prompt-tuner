import mesop as me

import components as mex
import handlers
from constants import DIALOG_INPUT_WIDTH
from helpers import find_prompt
from state import State
from state import Prompt


@me.component
def prompt_version_history():
  state = me.state(State)
  with mex.dialog(state.dialog_show_version_history):
    me.text("Version history", type="headline-6")
    me.select(
      label="Select Version",
      options=[
        me.SelectOption(label=f"v{prompt.version}", value=str(prompt.version))
        for prompt in state.prompts
      ],
      style=me.Style(width=DIALOG_INPUT_WIDTH),
      on_selection_change=on_select_version,
    )
    with mex.dialog_actions():
      me.button(
        "Close",
        key="dialog_show_version_history",
        on_click=handlers.on_close_dialog,
        style=me.Style(border_radius="10"),
      )


def on_select_version(e: me.SelectSelectionChangeEvent):
  """Update UI to show the selected prompt version and close the dialog."""
  state = me.state(State)
  selected_version = int(e.value)
  prompt = find_prompt(state.prompts, selected_version)
  if prompt != Prompt():
    state.prompt = prompt.prompt
    state.version = prompt.version
    state.system_instructions = prompt.system_instructions
    state.model = prompt.model
    state.model_temperature = prompt.model_temperature
    state.model_temperature_input = str(prompt.model_temperature)
    # If there is an existing response, select the most recent one.
    if prompt.responses:
      state.prompt_variables = prompt.responses[-1]["variables"]
      state.response = prompt.responses[-1]["output"]
    else:
      state.response = ""
    state.dialog_show_version_history = False
