from typing import Callable

import mesop as me

_NUM_REQUIRED_ROWS = 3


@me.component
def prompt_eval_table(prompt, on_select_rating: Callable | None = None):
  """Creates a grid table for displaying and comparing different prompt version runs."""
  # Add a row for each variable
  num_vars = len(prompt.variables)
  table_size = num_vars + _NUM_REQUIRED_ROWS
  with me.box(
    style=me.Style(
      border=me.Border.all(me.BorderSide(width=1, style="solid", color="#DEE2E6")),
      display="grid",
      grid_template_columns=f"1fr repeat({num_vars}, 20fr) 20fr 1fr"
      if num_vars
      else "1fr 20fr 1fr",
      margin=me.Margin.all(15),
      overflow_x="scroll",
    )
  ):
    # Render first row. This row only displays the Prompt version.
    for i in range(table_size):
      with me.box(
        style=me.Style(
          background="#FFF",
          border=me.Border.all(me.BorderSide(width=1, style="solid", color="#DEE2E6")),
          color="#000",
          font_size=15,
          font_weight="bold",
          padding=me.Padding.all(10),
        )
      ):
        if i == num_vars + 1:
          me.text(f"Version {prompt.version}")
        else:
          me.text("")

    # Render second row. This row only displays the headers of the table:
    # variable names, model response, avg rating.
    header_row = [""] + prompt.variables + ["Model response"] + [""]
    for i, header_text in enumerate(header_row):
      with me.box(
        style=me.Style(
          background="#FFF",
          border=me.Border.all(me.BorderSide(width=1, style="solid", color="#DEE2E6")),
          color="#0063FF" if header_text and header_text != "Model response" else "#444",
          font_size=13,
          font_weight="bold",
          padding=me.Padding.all(10),
        )
      ):
        # Handle the variable header case.
        if header_text and header_text != "Model response":
          me.text("{{" + header_text + "}}")
        elif i == table_size - 1:
          avg_rating = _calculate_avg_rating_from_prompt(prompt)
          if avg_rating is not None:
            with me.tooltip(message="Average rating"):
              me.text(f"{avg_rating:.2f}", style=me.Style(text_align="center"))
          else:
            me.text("")
        else:
          me.text(header_text)

    # Render the data rows by going through the prompt responses.
    for row_index, example in enumerate(prompt.responses):
      content_row = (
        [row_index]
        + [example["variables"][v] for v in prompt.variables]
        + [example["output"], example.get("rating", "")]
      )
      for col_index, content in enumerate(content_row):
        if col_index == len(content_row) - 1:
          with me.box(
            style=me.Style(
              background="#FFF",
              border=me.Border.all(me.BorderSide(width=1, style="solid", color="#DEE2E6")),
              color="#000",
              padding=me.Padding.all(10),
            )
          ):
            me.select(
              value=content,
              options=[
                me.SelectOption(label="1", value="1"),
                me.SelectOption(label="2", value="2"),
                me.SelectOption(label="3", value="3"),
                me.SelectOption(label="4", value="4"),
                me.SelectOption(label="5", value="5"),
              ],
              on_selection_change=on_select_rating,
              key=f"rating_{prompt.version}_{row_index}",
              style=me.Style(width=60),
            )
        elif col_index == 0 or not content:
          with me.box(
            style=me.Style(
              background="#FFF",
              border=me.Border.all(me.BorderSide(width=1, style="solid", color="#DEE2E6")),
              color="#000",
              font_size=14,
              padding=me.Padding.all(10),
              text_align="center",
            )
          ):
            me.text(str(content))
        else:
          with me.box(
            style=me.Style(
              background="#FFF",
              border=me.Border.all(me.BorderSide(width=1, style="solid", color="#DEE2E6")),
              color="#000",
              font_size=14,
              padding=me.Padding.all(10),
              max_height=300,
              min_width=300,
              overflow_y="scroll",
            )
          ):
            me.markdown(content)


def _calculate_avg_rating_from_prompt(prompt) -> float | None:
  ratings = [int(response["rating"]) for response in prompt.responses if response.get("rating")]
  if ratings:
    return sum(ratings) / float(len(ratings))
  return None
