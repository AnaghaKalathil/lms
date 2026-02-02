from frappe.utils.jinja import render_template
import subprocess
import tempfile
import os

def compile_mjml(mjml_content):
    with tempfile.NamedTemporaryFile(
        suffix=".mjml", delete=False
    ) as mjml_file:
        mjml_file.write(mjml_content.encode("utf-8"))
        mjml_path = mjml_file.name

    html_path = mjml_path.replace(".mjml", ".html")

    subprocess.run(
        ["mjml", mjml_path, "-o", html_path],
        check=True
    )

    with open(html_path, "r", encoding="utf-8") as f:
        html = f.read()

    os.remove(mjml_path)
    os.remove(html_path)

    return html


def render_mjml_template(mjml_template, context):
    """
    STEP 5 happens here:
    - Render Jinja
    - Compile MJML
    """
    # 1️⃣ Render Jinja variables
    rendered_mjml = render_template(mjml_template, context)

    # 2️⃣ Compile MJML → HTML
    return compile_mjml(rendered_mjml)
