from dataclasses import fields

import mesop as me


def merge_styles(default: me.Style, overrides: me.Style | None = None) -> me.Style:
  """Merges two styles together.

  Args:
    default: The starting style
    overrides: Any set styles will override styles in default
  """
  if not overrides:
    overrides = me.Style()

  default_fields = {field.name: getattr(default, field.name) for field in fields(me.Style)}
  override_fields = {
    field.name: getattr(overrides, field.name)
    for field in fields(me.Style)
    if getattr(overrides, field.name) is not None
  }

  return me.Style(**default_fields | override_fields)
