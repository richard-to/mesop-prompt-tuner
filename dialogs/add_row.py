import copy

import mesop as me

import components as mex
import handlers
import llm
from constants import DIALOG_INPUT_WIDTH
from helpers import parse_variables, find_prompt
from state import State


@me.component
def add_row():
  state = me.state(State)

  with mex.dialog(state.dialog_show_add_row):
    me.text("Add row", type="headline-6")
    if not state.prompt_variables:
      me.text("No variables defined in prompt.", style=me.Style(width=DIALOG_INPUT_WIDTH))
    else:
      with me.box(
        style=me.Style(display="flex", justify_content="end", margin=me.Margin(bottom=15))
      ):
        me.button(
          "Generate",
          on_click=on_click_generate_variables,
          style=me.Style(background="#EBF1FD", border_radius="10"),
        )
      variable_names = set(parse_variables(state.prompt))
      with me.box(style=me.Style(display="flex", flex_direction="column")):
        for name in state.prompt_variables.keys():
          if name not in variable_names:
            continue
          me.textarea(
            label=name,
            value=state.add_row_prompt_variables.get(name, ""),
            on_blur=on_input_variable,
            style=me.Style(width=DIALOG_INPUT_WIDTH),
            key=name,
          )

    with mex.dialog_actions():
      me.button(
        "Close",
        on_click=on_close_dialog,
        key="dialog_show_add_row",
        style=me.Style(border_radius="10"),
      )
      me.button("Add", type="flat", on_click=on_click_add_row, style=me.Style(border_radius="10"))


def on_close_dialog(e: me.ClickEvent):
  state = me.state(State)
  state.add_row_prompt_variables = {}
  handlers.on_close_dialog(e)


def on_click_add_row(e: me.ClickEvent):
  state = me.state(State)
  prompt = find_prompt(state.prompts, state.version)
  prompt.responses.append(
    {
      "variables": copy.copy(state.add_row_prompt_variables),
      "output": "",
      "rating": 0,
    }
  )
  state.add_row_prompt_variables = {}
  state.dialog_show_add_row = False


def on_input_variable(e: me.InputBlurEvent):
  """Generic event to save input variables."""
  state = me.state(State)
  state.add_row_prompt_variables[e.key] = e.value


def on_click_generate_variables(e: me.ClickEvent):
  """Generates values for the given empty variables."""
  state = me.state(State)
  variable_names = set(parse_variables(state.prompt))
  generated_variables = llm.generate_variables(
    state.prompt, variable_names, state.model, state.model_temperature
  )

  for name in state.prompt_variables:
    if name in variable_names and name in generated_variables:
      state.add_row_prompt_variables[name] = generated_variables[name]
