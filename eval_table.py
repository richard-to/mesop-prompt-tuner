from typing import Callable
import hashlib

import mesop as me

from state import Prompt
from web_components import markedjs_component


@me.component
def prompt_eval_table(
  prompts: list[Prompt],
  on_select_rating: Callable | None = None,
  on_click_run: Callable | None = None,
):
  data = _make_table_meta(prompts)
  response_map = _make_response_map(prompts)

  with me.box(
    style=me.Style(
      display="grid",
      grid_template_columns=" ".join([row.get("size", "1fr") for row in data]),
      overflow_x="scroll",
    )
  ):
    # Render first header row. This row only displays the Prompt version.
    for row in data:
      with me.box(style=_HEADER_STYLE):
        me.text(row.get("header_1", ""))

    # Render second header row.
    for row in data:
      with me.box(style=_HEADER_STYLE):
        if row["type"] == "model_rating":
          avg_rating = _calculate_avg_rating_from_prompt(row["prompt"])
          if avg_rating is not None:
            with me.tooltip(message="Average rating"):
              me.text(
                f"{avg_rating:.2f}",
                style=me.Style(
                  font_size=13, color=me.theme_var("on-surface-variant"), text_align="center"
                ),
              )
        elif row["type"] == "variable":
          me.text(
            row.get("header_2", ""), style=me.Style(font_size=13, color=me.theme_var("primary"))
          )
        else:
          me.text(
            row.get("header_2", ""),
            style=me.Style(font_size=13, color=me.theme_var("on-surface-variant")),
          )

    # Render examples
    for row_index, example in enumerate(prompts[0].responses):
      response_key = _make_variables_key(example["variables"])
      for row in data:
        if row["type"] == "index":
          with me.box(style=_INDEX_STYLE):
            me.text(str(row_index))
        elif row["type"] == "variable":
          with me.box(style=_MARKDOWN_BOX_STYLE):
            markedjs_component(example["variables"][row["variable_name"]])
        elif row["type"] == "model_response":
          with me.box(style=_MARKDOWN_BOX_STYLE):
            prompt_response = response_map[row["prompt"].version].get(response_key)
            if prompt_response and prompt_response[0]["output"]:
              markedjs_component(prompt_response[0]["output"])
            else:
              with me.box(
                style=me.Style(
                  display="flex", height="100%", justify_content="center", align_items="center"
                )
              ):
                response_index = prompt_response[1] if prompt_response else "-1"
                _, selected_version_response_index = response_map[prompts[0].version].get(
                  response_key
                )
                with me.content_button(
                  key=f"run_{row['prompt'].version}_{response_index}_{selected_version_response_index}",
                  on_click=on_click_run,
                  style=me.Style(
                    background=me.theme_var("secondary-container"),
                    color=me.theme_var("on-secondary-container"),
                    border_radius="10",
                  ),
                ):
                  with me.tooltip(message="Run prompt"):
                    me.icon("play_arrow")
        elif row["type"] == "model_rating":
          with me.box(style=_RATING_STYLE):
            prompt_response = response_map[row["prompt"].version].get(response_key)
            if prompt_response and prompt_response[0]["output"]:
              me.select(
                value=prompt_response[0].get("rating", 0),
                options=[
                  me.SelectOption(label="1", value="1"),
                  me.SelectOption(label="2", value="2"),
                  me.SelectOption(label="3", value="3"),
                  me.SelectOption(label="4", value="4"),
                  me.SelectOption(label="5", value="5"),
                ],
                on_selection_change=on_select_rating,
                key=f"rating_{row['prompt'].version}_{prompt_response[1]}",
                style=me.Style(width=60),
              )


def _hash_string(string: str) -> str:
  encoded_string = string.encode("utf-8")
  result = hashlib.md5(encoded_string)
  return result.hexdigest()


def _make_variables_key(variables: dict[str, str]) -> str:
  return _hash_string("--".join(variables.values()))


def _make_response_map(prompts: list[Prompt]) -> dict:
  prompt_map = {}
  for prompt in prompts:
    response_map = {}
    for response_index, response in enumerate(prompt.responses):
      key = _make_variables_key(response["variables"])
      response_map[key] = (response, response_index)
    prompt_map[prompt.version] = response_map
  return prompt_map


def _make_table_meta(prompts: list[Prompt]) -> dict:
  data = [
    {
      "type": "index",
    }
  ]
  for variable in prompts[0].variables:
    data.append(
      {
        "type": "variable",
        "header_2": "{{" + variable + "}}",
        "size": "20fr",
        "variable_name": variable,
      }
    )

  for i, prompt in enumerate(prompts):
    data.append(
      {
        "type": "model_response",
        "header_1": "Version " + str(prompt.version),
        "header_2": "Model response",
        "index": i,
        "size": "20fr",
        "prompt": prompt,
      }
    )
    data.append(
      {
        "type": "model_rating",
        "header_1": "",
        "header_2": "Rating",
        "prompt": prompt,
      }
    )
  return data


def _calculate_avg_rating_from_prompt(prompt: Prompt) -> float | None:
  ratings = [int(response["rating"]) for response in prompt.responses if response.get("rating")]
  if ratings:
    return sum(ratings) / float(len(ratings))
  return None


_BORDER_SIDE = me.BorderSide(width=1, style="solid", color=me.theme_var("outline-variant"))

_HEADER_STYLE = me.Style(
  background=me.theme_var("surface-container-lowest"),
  border=me.Border.all(_BORDER_SIDE),
  color=me.theme_var("on-surface"),
  font_size=15,
  font_weight="bold",
  padding=me.Padding.all(10),
)

_INDEX_STYLE = me.Style(
  background=me.theme_var("surface-container-lowest"),
  border=me.Border.all(_BORDER_SIDE),
  color=me.theme_var("on-surface"),
  font_size=14,
  padding=me.Padding.all(10),
  text_align="center",
)

_MARKDOWN_BOX_STYLE = me.Style(
  background=me.theme_var("surface-container-lowest"),
  border=me.Border.all(_BORDER_SIDE),
  color=me.theme_var("on-surface"),
  font_size=14,
  padding=me.Padding.all(10),
  max_height=300,
  min_width=300,
  overflow_y="scroll",
)

_RATING_STYLE = me.Style(
  background=me.theme_var("surface-container-lowest"),
  border=me.Border.all(_BORDER_SIDE),
  color=me.theme_var("on-surface"),
  padding=me.Padding.all(10),
)
