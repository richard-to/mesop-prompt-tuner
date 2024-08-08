import copy

import mesop as me
import mesop.labs as mel

import components as mex
import dialogs
import handlers
import llm
from eval_table import prompt_eval_table
from tool_sidebar import tool_sidebar
from helpers import find_prompt, parse_variables
from state import State, Prompt
from web_components import AsyncAction
from web_components import async_action_component
from web_components import markedjs_component

_INSTRUCTIONS = """
- Write your prompt.
  - You can use variables using this syntax `{{VARIABLE_NAME}}`.
- If you used variables, populate them from the `Set variables` dialog.
- Adjust model settings if necessary from the `Model settings` dialog.
- When you're ready, press the run button.
- If you make adjustments to your prompt or model settings, pressing run will create a
  new version of your prompt.
""".strip()


@me.page(
  stylesheets=[
    # Other themes here: https://www.jsdelivr.com/package/npm/highlight.js?tab=files&path=styles
    "https://cdn.jsdelivr.net/npm/highlight.js@11.10.0/styles/github-dark.min.css",
    "https://cdn.jsdelivr.net/npm/highlight.js@11.10.0/styles/github.min.css",
  ],
  security_policy=me.SecurityPolicy(
    allowed_script_srcs=[
      "https://cdn.jsdelivr.net",
    ],
    dangerously_disable_trusted_types=True,
    allowed_iframe_parents=["https://huggingface.co"],
  ),
)
def app():
  state = me.state(State)

  action = (
    AsyncAction(value=state.async_action_name, duration_seconds=state.async_action_duration)
    if state.async_action_name
    else None
  )
  async_action_component(action=action, on_finished=on_async_action_finished)

  mex.snackbar(is_visible=state.show_snackbar, label=state.snackbar_message)

  dialogs.update_title()
  dialogs.model_settings()
  dialogs.prompt_variables()
  dialogs.prompt_version_history()
  dialogs.add_comparisons()
  dialogs.generate_prompt()
  dialogs.load_prompt()
  dialogs.add_row()

  with me.box(
    style=me.Style(
      background=me.theme_var("surface-container-lowest"),
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
            on_blur=handlers.on_update_input,
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
          mex.button(
            "Generate prompt",
            disabled=bool(state.prompt),
            style=me.Style(
              background=me.theme_var("secondary-container"),
              color=me.theme_var("on-secondary-container"),
            ),
            on_click=handlers.on_open_dialog,
            key="dialog_show_generate_prompt",
          )

      with me.box(style=me.Style(padding=me.Padding.all(15), overflow_y="scroll")):
        if state.response:
          with mex.card(title="Response", style=me.Style(overflow_y="hidden")):
            markedjs_component(state.response)
        else:
          with mex.card(title="Prompt Tuner Instructions"):
            markedjs_component(_INSTRUCTIONS)
    else:
      # Render eval page
      with me.box(style=me.Style(grid_column="1 / -2", overflow_y="scroll")):
        prompt = find_prompt(state.prompts, state.version)
        if prompt:
          with me.box(style=me.Style(margin=me.Margin.all(15))):
            compare_prompts = [
              prompt for prompt in state.prompts if prompt.version in state.comparisons
            ]
            prompt_eval_table(
              [prompt] + compare_prompts,
              on_select_rating=on_select_rating,
              on_click_run=on_click_eval_run,
            )
            mex.button(
              label="Add row",
              type="flat",
              style=me.Style(
                margin=me.Margin(top=10),
              ),
              key="dialog_show_add_row",
              on_click=handlers.on_open_dialog,
            )
    tool_sidebar()


# Event handlers


def on_click_system_instructions_header(e: me.ClickEvent):
  """Open/close system instructions card."""
  state = me.state(State)
  state.system_prompt_card_expanded = not state.system_prompt_card_expanded


def on_click_eval_run(e: me.ClickEvent):
  state = me.state(State)
  _, prompt_version, response_index, selected_prompt_response_index = e.key.split("_")
  prompt = find_prompt(state.prompts, int(prompt_version))
  selected_prompt = find_prompt(state.prompts, state.version)
  selected_prompt

  if response_index != "-1":
    response = prompt.responses[int(response_index)]
  else:
    response = {
      "variables": copy.copy(
        selected_prompt.responses[int(selected_prompt_response_index)]["variables"]
      ),
      "rating": 0,
    }
    prompt.responses.append(response)

  prompt_text = prompt.prompt
  for name, value in response["variables"].items():
    prompt_text = prompt_text.replace("{{" + name + "}}", value)
  response["output"] = llm.run_prompt(
    prompt_text, prompt.system_instructions, prompt.model, prompt.model_temperature
  )


def on_click_run(e: me.ClickEvent):
  """Runs the prompt with the given variables.

  A new version of the prompt will be created if the prompt, system instructions, or
  model settings have changed.

  A new response will be added if the variables have been updated.
  """
  state = me.state(State)
  num_versions = len(state.prompts)
  if state.version:
    current_prompt_meta = state.prompts[state.version - 1]
  else:
    current_prompt_meta = Prompt()

  variable_names = set(parse_variables(state.prompt))
  prompt_variables = {
    name: value for name, value in state.prompt_variables.items() if name in variable_names
  }

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
  for name, value in prompt_variables.items():
    prompt = prompt.replace("{{" + name + "}}", value)
  state.response = llm.run_prompt(
    prompt, state.system_instructions, state.model, state.model_temperature
  )
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
  variable_names = parse_variables(state.prompt)
  for variable_name in variable_names:
    if variable_name not in state.prompt_variables:
      state.prompt_variables[variable_name] = ""


def on_click_mode_toggle(e: me.ClickEvent):
  """Toggle between Prompt and Eval modes."""
  state = me.state(State)
  state.mode = "Eval" if state.mode == "Prompt" else "Prompt"


def on_select_rating(e: me.SelectSelectionChangeEvent):
  state = me.state(State)
  _, prompt_version, response_index = e.key.split("_")
  prompt = find_prompt(state.prompts, int(prompt_version))
  prompt.responses[int(response_index)]["rating"] = e.value


def on_async_action_finished(e: mel.WebEvent):
  state = me.state(State)
  state.async_action_name = ""
  state.snackbar_message = ""
  state.show_snackbar = False


# Style helpers

_STYLE_INVISIBLE_TEXTAREA = me.Style(
  background=me.theme_var("surface-container-lowest"),
  color=me.theme_var("on-surface"),
  overflow_y="hidden",
  width="100%",
  outline="none",
  border=me.Border.all(me.BorderSide(style="none")),
)
