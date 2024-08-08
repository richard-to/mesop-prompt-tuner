import mesop as me
import mesop.labs as mel


@mel.web_component(path="./markedjs_component.js")
def markedjs_component(
  markdown: str,
  light_mode_theme: str = "https://cdn.jsdelivr.net/npm/highlight.js@11.10.0/styles/github.min.css",
  dark_mode_theme: str = "https://cdn.jsdelivr.net/npm/highlight.js@11.10.0/styles/github-dark.min.css",
):
  return mel.insert_web_component(
    name="markedjs-component",
    properties={
      "markdown": markdown,
      "themeBrightness": me.theme_brightness(),
      "lightModeTheme": light_mode_theme,
      "darkModeTheme": dark_mode_theme,
    },
  )
