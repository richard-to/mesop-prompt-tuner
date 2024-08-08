import json
from dataclasses import asdict, dataclass
from typing import Any, Callable

import mesop.labs as mel


@dataclass
class AsyncAction:
  value: str
  duration_seconds: int


@mel.web_component(path="./async_action_component.js")
def async_action_component(
  *,
  action: AsyncAction | None = None,
  on_started: Callable[[mel.WebEvent], Any] | None = None,
  on_finished: Callable[[mel.WebEvent], Any] | None = None,
  key: str | None = None,
):
  """Creates an invisibe component that will delay state changes asynchronously.

  Right now this implementation is limited since we basically just pass the key around.
  But ideally we also pass in some kind of value to update when the time out expires.

  The main benefit of this component is for cases, such as status messages that may
  appear and disappear after some duration. The primary example here is the example
  snackbar widget, which right now blocks the UI when using the sleep yield approach.

  The other benefit of this component is that it works generically (rather than say
  implementing a custom snackbar widget as a web component).
  """
  events = {
    "startedEvent": on_started,
    "finishedEvent": on_finished,
  }
  return mel.insert_web_component(
    name="async-action-component",
    key=key,
    events={key: value for key, value in events.items() if value is not None},
    properties={"action": json.dumps(asdict(action)) if action else ""},
  )
