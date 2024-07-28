import re
from state import Prompt


_RE_VARIABLES = re.compile(r"\{\{(\w+)\}\}")


def parse_variables(prompt: str) -> list[str]:
  return _RE_VARIABLES.findall(prompt)


def find_prompt(prompts: list[Prompt], version: int) -> Prompt:
  # We don't expect too many versions, so we'll just loop through the list to find the
  # right version.
  for prompt in prompts:
    if prompt.version == version:
      return prompt
  return Prompt()
