
import frappe

def apply_frontend_template(doc, method):
    """
    Validate frontend-built template link only.
    NO html injection here.
    """

    if not doc.custom_email_template:
        return

    template = frappe.get_doc("Email Template", doc.custom_email_template)

    # Ensure template has HTML
    if not template.response_html:
        frappe.throw("Selected Email Template has no HTML content")

    if not template.get("from_builder"):
        return

    doc.message = template.response_html

    # if not doc.subject:
    #     doc.subject = template.subject

