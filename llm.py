import os

import google.generativeai as genai


GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

genai.configure(api_key=GOOGLE_API_KEY)

# TODO: Improve on this prompt. Just adding something simple for testing.
_GENERATE_PROMPT = """
Write a detailed prompt to help complete the between <task></task> block.

<task>
{task}
</task>

For custom user input, you can leave placeholder variables. For example, if you have
variable named EMAIL, it would like {{{{EMAIL}}}} in the resulting prompt.
""".strip()


def _make_model(model_name: str, temperature: float) -> genai.GenerativeModel:
  return genai.GenerativeModel(
    model_name,
    generation_config={
      "temperature": temperature,
      "top_p": 0.95,
      "top_k": 64,
      "max_output_tokens": 16384,
    },
  )


def generate_prompt(task_description: str, model_name: str, temperature: float) -> str:
  model = _make_model(model_name, temperature)
  prompt = _GENERATE_PROMPT.format(task=task_description)
  return model.generate_content(prompt).text


def generate_variables(
  prompt: str, variables: dict[str, str], model_name: str, temperature: float
) -> dict[str, str]:
  # model = _make_model(model_name, temperature)
  pass


def run_prompt(prompt_with_variables: str, model_name: str, temperature: float) -> str:
  model = _make_model(model_name, temperature)
  return model.generate_content(prompt_with_variables).text
