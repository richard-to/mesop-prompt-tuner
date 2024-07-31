from dataclasses import asdict
import errno
import json
import os
import re
import time

import mesop as me

import components as mex
import handlers
from constants import SAVED_PROMPT_DIRECTORY
from state import State


@me.component
def tool_sidebar():
  state = me.state(State)
  with mex.icon_sidebar():
    if state.mode == "Prompt":
      mex.icon_menu_item(
        icon="tune",
        tooltip="Model settings",
        key="dialog_show_model_settings",
        on_click=handlers.on_open_dialog,
      )
      mex.icon_menu_item(
        icon="data_object",
        tooltip="Set variables",
        key="dialog_show_prompt_variables",
        on_click=handlers.on_open_dialog,
      )
    mex.icon_menu_item(
      icon="history",
      tooltip="Version history",
      key="dialog_show_version_history",
      on_click=handlers.on_open_dialog,
    )

    if state.mode == "Eval":
      mex.icon_menu_item(
        icon="compare",
        tooltip="Compare versions",
        key="dialog_show_add_comparison",
        on_click=handlers.on_open_dialog,
      )

    mex.icon_menu_item(
      icon="upload",
      tooltip="Load prompt data",
      key="dialog_show_load",
      on_click=handlers.on_open_dialog,
    )

    mex.icon_menu_item(
      icon="download",
      tooltip="Download prompt data",
      on_click=on_click_download,
    )

    mex.icon_menu_item(
      icon="light_mode" if me.theme_brightness() == "dark" else "dark_mode",
      tooltip="Switch to " + ("light mode" if me.theme_brightness() == "dark" else "dark mode"),
      on_click=on_click_theme_brightness,
    )


def on_click_theme_brightness(e: me.ClickEvent):
  if me.theme_brightness() == "light":
    me.set_theme_mode("dark")
  else:
    me.set_theme_mode("light")


def on_click_download(e: me.ClickEvent):
  state = me.state(State)
  cleaned_title = _clean_title(state.title)
  filename = f"prompt-{cleaned_title}.json"
  _create_directory(SAVED_PROMPT_DIRECTORY)

  with open(f"{SAVED_PROMPT_DIRECTORY}/{filename}", "w") as outfile:
    output = {
      key: value
      for key, value in asdict(state).items()
      if key
      not in (
        "temp_title",
        "mode",
        "comparisons",
        "system_prompt_card_expanded",
        "prompt_gen_task_description",
      )
      and not key.startswith("dialog_")
    }
    json.dump(output, outfile)

  state.snackbar_message = f"Prompt exported as {filename}."
  state.show_snackbar = True
  yield
  time.sleep(state.snackbar_duration)
  yield
  state.show_snackbar = False
  yield


def _clean_title(title: str) -> str:
  return re.sub(r"[^a-z0-9_]", "", title.lower().replace(" ", "_"))


def _create_directory(directory_path):
  """Creates a directory if it doesn't exist."""
  try:
    os.makedirs(directory_path)
  except OSError as e:
    if e.errno != errno.EEXIST:
      raise
