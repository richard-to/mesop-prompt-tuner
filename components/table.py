import mesop as me

_NUM_REQUIRED_ROWS = 3


@me.component
def prompt_eval_table(prompt):
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
    )
  ):
    # Render first row. This row only displays the Prompt version.
    for i in range(table_size):
      with me.box(
        style=me.Style(
          background="#fff",
          border=me.Border.all(me.BorderSide(width=1, style="solid", color="#DEE2E6")),
          color="#000",
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
    for header_text in header_row:
      with me.box(
        style=me.Style(
          background="#FFF",
          border=me.Border.all(me.BorderSide(width=1, style="solid", color="#DEE2E6")),
          color="#0063FF" if header_text and header_text != "Model response" else "#333",
          padding=me.Padding.all(10),
        )
      ):
        # Handle the variable header case.
        if header_text and header_text != "Model response":
          me.text("{{" + header_text + "}}")
        else:
          me.text(header_text)

    # Render the data rows by going through the prompt responses.
    for index, example in enumerate(prompt.responses):
      content_row = (
        [index]
        + [example["variables"][v] for v in prompt.variables]
        + [example["output"], example.get("rating", "")]
      )
      for row in content_row:
        with me.box(
          style=me.Style(
            background="#fff",
            border=me.Border.all(me.BorderSide(width=1, style="solid", color="#DEE2E6")),
            color="#000",
            padding=me.Padding.all(10),
          )
        ):
          me.text(row)
