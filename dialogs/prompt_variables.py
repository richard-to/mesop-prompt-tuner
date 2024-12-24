import mesop as me

import components as mex
import handlers
import llm
from constants import DIALOG_INPUT_WIDTH
from helpers import parse_variables
from state import State


@me.component
def prompt_variables():
  state = me.state(State)

  with mex.dialog(state.dialog_show_prompt_variables):
    me.text("Prompt Variables", type="headline-6")
    if not state.prompt_variables:
      me.text("No variables defined in prompt.", style=me.Style(width=DIALOG_INPUT_WIDTH))
    else:
      variable_names = set(parse_variables(state.prompt))
      with me.box(style=me.Style(display="flex", flex_direction="column")):
        for name, value in state.prompt_variables.items():
          if name not in variable_names:
            continue
          me.textarea(
            label=name,
            value=value,
            on_blur=on_input_variable,
            style=me.Style(width=DIALOG_INPUT_WIDTH),
            key=name,
          )

    with mex.dialog_actions():
      mex.button(
        "Close",
        on_click=handlers.on_close_dialog,
        key="dialog_show_prompt_variables",
      )


def on_input_variable(e: me.InputBlurEvent):
  """Generic event to save input variables.

  TODO: Probably should prefix the key to avoid key collisions.
  """
  state = me.state(State)
  state.prompt_variables[e.key] = e.value


def on_click_generate_variables(e: me.ClickEvent):
  """Generates values for the given empty variables."""
  state = me.state(State)
  variable_names = set(parse_variables(state.prompt))
  generated_variables = llm.generate_variables(
    state.prompt, variable_names, state.model, state.model_temperature
  )
  for name in state.prompt_variables:
    if name in variable_names and name in generated_variables:
      state.prompt_variables[name] = generated_variables[name]
