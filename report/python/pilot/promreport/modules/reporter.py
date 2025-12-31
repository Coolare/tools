import os
from jinja2 import Environment, FileSystemLoader
import base64

def font_data_uri(font_path):
    if not font_path or not os.path.exists(font_path):
        return ""
    with open(font_path, "rb") as f:
        b = base64.b64encode(f.read()).decode("utf-8")
    ext = os.path.splitext(font_path)[1].lower()
    mime = "font/ttf"
    if ext == ".otf":
        mime = "font/otf"
    return f"data:{mime};base64,{b}"

def render_html(template_path, context, output_path):
    env = Environment(loader=FileSystemLoader(os.path.dirname(template_path)))
    tpl = env.get_template(os.path.basename(template_path))
    html = tpl.render(**context)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)
    return output_path