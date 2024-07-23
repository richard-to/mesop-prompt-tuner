import json
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

_GENERATE_VARIABLES_PROMPT = """
Your job is to generate data for the given placeholders: {placeholders}.

The generated data should reflect the name of the placeholder.

Render the output as JSON.

Here is an example output for these placeholders: STORY, FEEDBACK_TYPE

{{
  "STORY": "Generated data for a story",
  "FEEDBACK_TYPE": "Type of feedback to provide on the story"
}}

Again, please generate outputs for these placeholders: {placeholders}
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
  prompt: str, variable_names: list[str], model_name: str, temperature: float
) -> dict[str, str]:
  model = _make_model(model_name, temperature)
  output = (
    model.generate_content(
      _GENERATE_VARIABLES_PROMPT.format(placeholders=", ".join(variable_names))
    )
    .text.removeprefix("```json")
    .removesuffix("```")
  )
  return json.loads(output)


def run_prompt(prompt_with_variables: str, model_name: str, temperature: float) -> str:
  model = _make_model(model_name, temperature)
  return model.generate_content(prompt_with_variables).text
