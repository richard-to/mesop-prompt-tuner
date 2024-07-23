from dataclasses import dataclass, field
import re

import mesop as me

import components as mex

_DIALOG_INPUT_WIDTH = 350

_MODEL_TEMPERATURE_MAX = 2
_MODEL_TEMPERATURE_MIN = 0

_INSTRUCTIONS = """
- Write your prompt.
  - You can use variables using this syntax `{{VARIABLE_NAME}}`.
- If you used variables, populate them from the `Set variables` dialog.
- Adjust model settings if necessary from the `Model settings` dialog.
- When you're ready, press the run button.
- If you make adjustments to your prompt or model settings, pressing run will create a
  new version of your prompt.
""".strip()

_RE_VARIABLES = re.compile(r"\{\{(\w+)\}\}")


@dataclass
class Prompt:
  prompt: str = ""
  model: str = ""
  model_temperature: float = 0.0
  system_instructions: str = ""
  version: int = 0
  variables: list[str] = field(default_factory=lambda: [])
  # Storing the responses as a dict to workaround bug with lists
  # of nested dataclass.
  responses: list[dict] = field(default_factory=lambda: [])


@me.stateclass
class State:
  # Main UI variables
  system_prompt_card_expanded: bool = False
  title: str = "Untitled Prompt"
  temp_title: str
  system_instructions: str
  prompt: str
  response: str
  version: int = 0

  # Prompt variables
  prompt_variables: dict[str, str]

  # Model info
  model: str = "gemini-1.5-flash"
  model_temperature: float = 1.0
  model_temperature_input: str = "1.0"

  # Dialogs
  dialog_show_title: bool = False
  dialog_show_model_settings: bool = False
  dialog_show_prompt_variables: bool = False
  dialog_show_generate_prompt: bool = False
  dialog_show_version_history: bool = False
  prompts: list[Prompt]

  # LLM Generate functionality
  prompt_gen_task_description: str

  # Valid modes: Prompt or Eval
  mode: str = "Prompt"


@me.page()
def app():
  state = me.state(State)

  # Update prompt title dialog
  with mex.dialog(state.dialog_show_title):
    me.text("Update Prompt Title", type="headline-6")
    me.input(
      label="Title",
      value=state.temp_title,
      on_blur=on_update_input,
      key="temp_title",
      style=me.Style(width=_DIALOG_INPUT_WIDTH),
    )
    with mex.dialog_actions():
      me.button("Cancel", on_click=on_close_dialog, key="dialog_show_title")
      me.button("Save", type="flat", disabled=not state.temp_title.strip(), on_click=on_save_title)

  # Dialog for controlling Model settings
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
        style=me.Style(width=_DIALOG_INPUT_WIDTH),
        on_selection_change=on_update_input,
      )
    with me.box():
      me.text("Temperature", style=me.Style(font_weight="bold"))
      with me.box(style=me.Style(display="flex", gap=10, width=_DIALOG_INPUT_WIDTH)):
        me.slider(
          min=_MODEL_TEMPERATURE_MIN,
          max=_MODEL_TEMPERATURE_MAX,
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
        on_click=on_close_dialog,
      )

  # Dialog for setting variables
  with mex.dialog(state.dialog_show_prompt_variables):
    me.text("Prompt Variables", type="headline-6")
    if not state.prompt_variables:
      me.text("No variables defined in prompt.", style=me.Style(width=_DIALOG_INPUT_WIDTH))
    else:
      with me.box(
        style=me.Style(display="flex", justify_content="end", margin=me.Margin(bottom=15))
      ):
        me.button("Generate", type="flat", on_click=on_click_generate_variables)
      variable_names = set(_parse_variables(state.prompt))
      with me.box(style=me.Style(display="flex", flex_direction="column")):
        for name, value in state.prompt_variables.items():
          if name not in variable_names:
            continue
          me.textarea(
            label=name,
            value=value,
            on_blur=on_input_variable,
            style=me.Style(width=_DIALOG_INPUT_WIDTH),
            key=name,
          )

    with mex.dialog_actions():
      me.button("Close", on_click=on_close_dialog, key="dialog_show_prompt_variables")

  # Dialog for showing prompt version history
  with mex.dialog(state.dialog_show_version_history):
    me.text("Version history", type="headline-6")
    me.select(
      label="Select Version",
      options=[
        me.SelectOption(label=f"v{prompt.version}", value=str(prompt.version))
        for prompt in state.prompts
      ],
      style=me.Style(width=_DIALOG_INPUT_WIDTH),
      on_selection_change=on_select_version,
    )
    with mex.dialog_actions():
      me.button("Close", key="dialog_show_version_history", on_click=on_close_dialog)

  # Dialog for generating a prompt with LLM assistance
  # TODO: Integrate with LLM
  with mex.dialog(state.dialog_show_generate_prompt):
    me.text("Generate Prompt", type="headline-6")
    me.textarea(
      label="Describe your task",
      value=state.prompt_gen_task_description,
      on_blur=on_update_input,
      key="prompt_gen_task_description",
      style=me.Style(width=_DIALOG_INPUT_WIDTH),
    )
    with mex.dialog_actions():
      me.button("Close", key="dialog_show_generate_prompt", on_click=on_close_dialog)
      me.button("Generate", type="flat", on_click=on_click_generate_prompt)

  with me.box(
    style=me.Style(
      background="#FDFDFD",
      display="grid",
      grid_template_columns="50fr 50fr 1fr",
      grid_template_rows="1fr 50fr",
      height="100vh",
    )
  ):
    with me.box(style=me.Style(grid_column="1 / -1")):
      with mex.header(max_width=None):
        with mex.header_section():
          with me.box(on_click=on_click_title, style=me.Style(cursor="pointer")):
            me.text(
              state.title,
              style=me.Style(font_size=16, font_weight="bold"),
            )
          if state.version:
            me.text(f"v{state.version}")

        with mex.header_section():
          mex.button_toggle(
            labels=["Prompt", "Eval"], selected=state.mode, on_click=on_click_mode_toggle
          )

    if state.mode == "Prompt":
      # Render prompt creation page
      with me.box(
        style=me.Style(padding=me.Padding(left=15, top=15, bottom=15), overflow_y="scroll")
      ):
        with mex.expanable_card(
          title="System Instructions",
          expanded=state.system_prompt_card_expanded,
          on_click_header=on_click_system_instructions_header,
        ):
          me.native_textarea(
            autosize=True,
            min_rows=2,
            placeholder="Optional tone and style instructions for the model",
            value=state.system_instructions,
            on_blur=on_update_input,
            style=_STYLE_INVISIBLE_TEXTAREA,
            key="system_instructions",
          )

        with mex.card(title="Prompt"):
          me.native_textarea(
            autosize=True,
            min_rows=2,
            placeholder="Enter your prompt",
            value=state.prompt,
            on_blur=on_update_prompt,
            style=_STYLE_INVISIBLE_TEXTAREA,
            key="prompt",
          )

        with me.box(
          style=me.Style(align_items="center", display="flex", justify_content="space-between")
        ):
          with me.content_button(
            type="flat",
            disabled=not state.prompt,
            on_click=on_click_run,
            style=me.Style(border_radius="10"),
          ):
            with me.tooltip(message="Run prompt"):
              me.icon("play_arrow")
          me.button(
            "Generate prompt",
            disabled=bool(state.prompt),
            style=me.Style(background="#EBF1FD", border_radius="10"),
            on_click=on_open_dialog,
            key="dialog_show_generate_prompt",
          )

      with me.box(style=me.Style(padding=me.Padding.all(15))):
        if state.response:
          with mex.card(title="Response", style=me.Style(height="100%")):
            me.markdown(state.response)
        else:
          with mex.card(title="Prompt Tuner Instructions", style=me.Style(height="100%")):
            me.markdown(_INSTRUCTIONS)
    else:
      # Render eval page
      with me.box(style=me.Style(grid_column="1 / -2")):
        prompt = _find_prompt(state.prompts, state.version)
        if prompt:
          mex.prompt_eval_table(prompt)

    with mex.icon_sidebar():
      if state.mode == "Prompt":
        mex.icon_menu_item(
          icon="tune",
          tooltip="Model settings",
          key="dialog_show_model_settings",
          on_click=on_open_dialog,
        )
        mex.icon_menu_item(
          icon="data_object",
          tooltip="Set variables",
          key="dialog_show_prompt_variables",
          on_click=on_open_dialog,
        )
      mex.icon_menu_item(
        icon="history",
        tooltip="Version history",
        key="dialog_show_version_history",
        on_click=on_open_dialog,
      )
      if state.mode == "Prompt":
        mex.icon_menu_item(icon="code", tooltip="Get code")


# Event handlers


def on_click_system_instructions_header(e: me.ClickEvent):
  """Open/close system instructions card."""
  state = me.state(State)
  state.system_prompt_card_expanded = not state.system_prompt_card_expanded


def on_click_run(e: me.ClickEvent):
  state = me.state(State)
  num_versions = len(state.prompts)
  if state.version:
    current_prompt_meta = state.prompts[state.version - 1]
  else:
    current_prompt_meta = Prompt()

  variable_names = set(_parse_variables(state.prompt))
  prompt_variables = {k: v for k, v in state.prompt_variables.items() if k in variable_names}

  if (
    current_prompt_meta.prompt != state.prompt
    or current_prompt_meta.system_instructions != state.system_instructions
    or current_prompt_meta.model != state.model
    or current_prompt_meta.model_temperature != state.model_temperature
  ):
    new_version = num_versions + 1
    state.prompts.append(
      Prompt(
        version=new_version,
        prompt=state.prompt,
        system_instructions=state.system_instructions,
        model=state.model,
        model_temperature=state.model_temperature,
        variables=list(variable_names),
      )
    )
    state.version = new_version

  prompt = state.prompt
  for k, v in prompt_variables.items():
    prompt = prompt.replace("{{" + k + "}}", v)
  state.response = "Version v" + str(state.version) + "\n\n" + prompt
  state.prompts[-1].responses.append(dict(output=state.response, variables=prompt_variables))


def on_click_title(e: me.ClickEvent):
  """Show dialog for editing the title of the prompt."""
  state = me.state(State)
  state.temp_title = state.title
  state.dialog_show_title = True


def on_update_prompt(e: me.InputBlurEvent):
  """Saves the prompt.

  Any new variables will be extracted from the prompt and added to prompt variables in
  the variables dialog.
  """
  state = me.state(State)
  state.prompt = e.value.strip()
  variable_names = _parse_variables(state.prompt)
  for variable_name in variable_names:
    if variable_name not in state.prompt_variables:
      state.prompt_variables[variable_name] = ""


def on_save_title(e: me.InputBlurEvent):
  """Saves the title and closes the dialog."""
  state = me.state(State)
  if state.temp_title:
    state.title = state.temp_title
    state.dialog_show_title = False


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
    if _MODEL_TEMPERATURE_MIN <= model_temperature <= _MODEL_TEMPERATURE_MAX:
      state.model_temperature = model_temperature
  except ValueError:
    pass


def on_input_variable(e: me.InputBlurEvent):
  """Generic event to save input variables.

  TODO: Probably should prefix the key to avoid key collisions.
  """
  state = me.state(State)
  state.prompt_variables[e.key] = e.value


def on_select_version(e: me.SelectSelectionChangeEvent):
  """Update UI to show the selected prompt version and close the dialog."""
  state = me.state(State)
  selected_version = int(e.value)
  prompt = _find_prompt(state.prompts, selected_version)
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


def on_click_generate_prompt(e: me.ClickEvent):
  """Generates an improved prompt based on the given task description and closes dialog.

  TODO: Implement this logic.
  """
  state = me.state(State)
  state.prompt = state.prompt_gen_task_description + " Improve prompt stuff here"
  state.dialog_show_generate_prompt = False


def on_click_generate_variables(e: me.ClickEvent):
  """Generates values for the given empty variables.

  TODO: Implement this logic.
  """
  state = me.state(State)
  variable_names = set(_parse_variables(state.prompt))
  for name, value in state.prompt_variables.items():
    if name in variable_names and not value:
      state.prompt_variables[name] = "Generate variable " + name


def on_click_mode_toggle(e: me.ClickEvent):
  """Toggle between Prompt and Eval modes."""
  state = me.state(State)
  state.mode = "Eval" if state.mode == "Prompt" else "Prompt"


# Generic event handlers


def on_open_dialog(e: me.ClickEvent):
  """Generic event to open a dialog."""
  state = me.state(State)
  setattr(state, e.key, True)


def on_close_dialog(e: me.ClickEvent):
  """Generic event to close a dialog."""
  state = me.state(State)
  setattr(state, e.key, False)


def on_update_input(e: me.InputBlurEvent | me.SelectSelectionChangeEvent):
  """Generic event to update input/select values."""
  state = me.state(State)
  setattr(state, e.key, e.value)


# Helper functions


def _parse_variables(prompt: str) -> list[str]:
  return _RE_VARIABLES.findall(prompt)


def _find_prompt(prompts: list[Prompt], version: int) -> Prompt:
  # We don't expected too many versions, so we'll just loop through the list to find the
  # right version.
  for prompt in prompts:
    if prompt.version == version:
      return prompt
  return Prompt()


# Style helpers

_STYLE_INVISIBLE_TEXTAREA = me.Style(
  overflow_y="hidden",
  width="100%",
  outline="none",
  border=me.Border.all(me.BorderSide(style="none")),
)
