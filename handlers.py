import mesop as me
from state import State


def on_open_dialog(e: me.ClickEvent):
  """Generic event to open a dialog."""
  state = me.state(State)
  setattr(state, e.key, True)


def on_close_dialog(e: me.ClickEvent):
  """Generic event to close a dialog."""
  state = me.state(State)
  setattr(state, e.key, False)


def on_update_input(e: me.InputBlurEvent | me.InputEvent | me.InputEnterEvent):
  """Generic event to update input values."""
  state = me.state(State)
  setattr(state, e.key, e.value)


def on_update_selection(e: me.SelectSelectionChangeEvent):
  """Generic event to update input values."""
  state = me.state(State)
  setattr(state, e.key, e.value)
