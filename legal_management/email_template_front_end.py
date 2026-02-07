import frappe
import subprocess
from frappe import _
from frappe.utils import get_url

def compile_mjml_to_html(mjml_content):
    """Compile MJML string to HTML"""
    result = subprocess.run(
        ["mjml", "-s", "-i"],  # -s = stdout, -i = stdin
        input=mjml_content.encode("utf-8"),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    if result.returncode != 0:
        frappe.throw(_("MJML compile error: {0}").format(result.stderr.decode()))
    return result.stdout.decode("utf-8")

@frappe.whitelist(allow_guest=True)
def create_from_frontend(template_name, html):
    frappe.log_error(f"Received HTML length: {len(html)}", "template_debug")
    if not template_name:
        frappe.throw("Template name is required")
    if not html:
        frappe.throw("HTML is required")

    if frappe.db.exists("Email Template", template_name):
        frappe.throw(_("Template with this name already exists"))

    html = compile_mjml_to_html(mjml_source)

    # Replace local /files/ with absolute URLs
    
    html_content = html.replace('src="/files/', f'src="{get_url("/files")}/')


    doc = frappe.get_doc({
        "doctype": "Email Template",
        "template_name": template_name,
        "name":template_name,
        "subject": template_name,
        "mjml_source": html_content,
        "response_html": html_content
    })

    doc.insert(ignore_permissions=True)
    frappe.db.commit()

    return {"message": f"Email Template {template_name} created successfully"}
