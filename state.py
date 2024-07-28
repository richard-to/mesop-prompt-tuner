from dataclasses import dataclass, field

import mesop as me


@dataclass
class Prompt:
  prompt: str = ""
  model: str = ""
  model_temperature: float = 0.0
  system_instructions: str = ""
  version: int = 0
  variables: list[str] = field(default_factory=list)
  # Storing the responses as a dict to workaround bug with lists
  # of nested dataclass.
  #
  # Keys: output, variables, rating
  responses: list[dict] = field(default_factory=list)


@me.stateclass
class State:
  # Main UI variables
  system_prompt_card_expanded: bool = False
  title: str = "Untitled Prompt"
  temp_title: str
  system_instructions: str
  prompt: str
  response: str
  version: int = 0

  # Prompt variables
  prompt_variables: dict[str, str]

  # Model info
  model: str = "gemini-1.5-flash"
  model_temperature: float = 1.0
  model_temperature_input: str = "1.0"

  # Dialogs
  dialog_show_title: bool = False
  dialog_show_model_settings: bool = False
  dialog_show_prompt_variables: bool = False
  dialog_show_generate_prompt: bool = False
  dialog_show_version_history: bool = False
  dialog_show_add_comparison: bool = False
  dialog_show_load: bool = False

  prompts: list[Prompt]

  # LLM Generate functionality
  prompt_gen_task_description: str

  # Valid modes: Prompt or Eval
  mode: str = "Prompt"

  comparisons: list[int]
