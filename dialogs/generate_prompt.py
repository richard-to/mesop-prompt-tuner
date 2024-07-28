import mesop as me

import components as mex
import handlers
import llm
from constants import DIALOG_INPUT_WIDTH
from helpers import parse_variables
from state import State


@me.component
def generate_prompt():
  state = me.state(State)
  with mex.dialog(state.dialog_show_generate_prompt):
    me.text("Generate Prompt", type="headline-6")
    me.textarea(
      label="Describe your task",
      value=state.prompt_gen_task_description,
      on_blur=handlers.on_update_input,
      key="prompt_gen_task_description",
      style=me.Style(width=DIALOG_INPUT_WIDTH),
    )
    with mex.dialog_actions():
      mex.button(
        "Close",
        key="dialog_show_generate_prompt",
        on_click=handlers.on_close_dialog,
      )
      mex.button(
        "Generate",
        type="flat",
        on_click=on_click_generate_prompt,
      )


def on_click_generate_prompt(e: me.ClickEvent):
  """Generates an improved prompt based on the given task description and closes dialog."""
  state = me.state(State)
  state.prompt = llm.generate_prompt(
    state.prompt_gen_task_description, state.model, state.model_temperature
  )
  variable_names = parse_variables(state.prompt)
  for variable_name in variable_names:
    if variable_name not in state.prompt_variables:
      state.prompt_variables[variable_name] = ""

  state.dialog_show_generate_prompt = False
