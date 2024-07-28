import json

import mesop as me

import components as mex
import handlers
from constants import DIALOG_INPUT_WIDTH
from state import State
from state import Prompt


@me.component
def load_prompt():
  state = me.state(State)
  with mex.dialog(state.dialog_show_load):
    with me.box(style=me.Style(width=DIALOG_INPUT_WIDTH)):
      me.text("Upload saved prompt", type="headline-6")
      me.uploader(
        label="Upload",
        accepted_file_types=["application/json"],
        type="flat",
        color="primary",
        on_upload=on_upload_prompt,
        style=me.Style(font_weight="bold", border_radius=10),
      )
      with mex.dialog_actions():
        me.button(
          "Close",
          key="dialog_show_load",
          on_click=handlers.on_close_dialog,
          style=me.Style(border_radius="10"),
        )


def on_upload_prompt(e: me.UploadEvent):
  state = me.state(State)
  data = json.loads(e.file.getvalue())
  data["prompts"] = [Prompt(**raw_prompt) for raw_prompt in data["prompts"]]
  for key, value in data.items():
    setattr(state, key, value)
  state.dialog_show_load = False
