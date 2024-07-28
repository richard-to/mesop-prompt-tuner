from dataclasses import asdict
import errno
import json
import os
import re

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
      key="dialog_show_download",
      on_click=on_click_download,
    )


def on_click_download(e: me.ClickEvent):
  state = me.state(State)
  cleaned_title = _clean_title(state.title)
  _create_directory(SAVED_PROMPT_DIRECTORY)

  with open(f"{SAVED_PROMPT_DIRECTORY}/prompt-{cleaned_title}.json", "w") as outfile:
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


def _clean_title(title: str) -> str:
  return re.sub(r"[^a-z0-9_]", "", title.lower().replace(" ", "_"))


def _create_directory(directory_path):
  """Creates a directory if it doesn't exist."""
  try:
    os.makedirs(directory_path)
    print(f"Directory '{directory_path}' created successfully.")
  except OSError as e:
    if e.errno != errno.EEXIST:
      raise