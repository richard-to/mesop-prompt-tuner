import mesop as me

import components as mex
import handlers
from constants import DIALOG_INPUT_WIDTH
from constants import MODEL_TEMPERATURE_MAX
from constants import MODEL_TEMPERATURE_MIN
from state import State


@me.component
def model_settings():
  state = me.state(State)
  with mex.dialog(state.dialog_show_model_settings):
    me.text("Model Settings", type="headline-6")
    with me.box():
      me.select(
        label="Model",
        key="model",
        options=[
          me.SelectOption(label="Gemini 1.5 Flash", value="gemini-1.5-flash"),
          me.SelectOption(label="Gemini 1.5 Pro", value="gemini-1.5-pro"),
        ],
        value=state.model,
        style=me.Style(width=DIALOG_INPUT_WIDTH),
        on_selection_change=handlers.on_update_selection,
      )
    with me.box():
      me.text("Temperature", style=me.Style(font_weight="bold"))
      with me.box(style=me.Style(display="flex", gap=10, width=DIALOG_INPUT_WIDTH)):
        me.slider(
          min=MODEL_TEMPERATURE_MIN,
          max=MODEL_TEMPERATURE_MAX,
          step=0.1,
          style=me.Style(width=260),
          on_value_change=on_slider_temperature,
          value=state.model_temperature,
        )
        me.input(
          value=state.model_temperature_input,
          on_input=on_input_temperature,
          style=me.Style(width=60),
        )

    with mex.dialog_actions():
      me.button(
        "Close",
        key="dialog_show_model_settings",
        on_click=handlers.on_close_dialog,
        style=me.Style(border_radius="10"),
      )


def on_slider_temperature(e: me.SliderValueChangeEvent):
  """Adjust temperature slider value."""
  state = me.state(State)
  state.model_temperature = float(e.value)
  state.model_temperature_input = str(state.model_temperature)


def on_input_temperature(e: me.InputEvent):
  """Adjust temperature slider value by input."""
  state = me.state(State)
  try:
    model_temperature = float(e.value)
    if MODEL_TEMPERATURE_MIN <= model_temperature <= MODEL_TEMPERATURE_MAX:
      state.model_temperature = model_temperature
  except ValueError:
    pass
