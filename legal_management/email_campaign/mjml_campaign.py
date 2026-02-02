import frappe
from legal_management.utils.mjml import render_mjml_template

@frappe.whitelist()
def preview_mjml_template(template_name, lead_name=None):
    template = frappe.get_doc("MJML Email Template", template_name)

    lead = frappe.get_doc("Lead", lead_name) if lead_name else None

    html = render_mjml_template(
        template.mjml_content,
        {
            "lead": lead,
            "campaign_name": "Sample Campaign",
            "unsubscribe_link": frappe.utils.get_url("/unsubscribe")
        }
    )

    return html or "<h3>No HTML generated</h3>"


@frappe.whitelist()
def compile_and_attach_mjml(campaign_name):
    campaign = frappe.get_doc("Email Campaign", campaign_name)

    if not campaign.mjml_template:
        frappe.throw("Please select an MJML Email Template")

    template = frappe.get_doc("MJML Email Template", campaign.mjml_template)

    # 🔥 SINGLE SOURCE OF TRUTH
    html = render_mjml_template(
        template.mjml_content,
        {
            "campaign": campaign,
            "unsubscribe_link": frappe.utils.get_url("/unsubscribe")
        }
    )

    if not html:
        frappe.throw("MJML compilation returned empty HTML")

    campaign.html_content = html
    campaign.save(ignore_permissions=True)

    return "MJML compiled and attached successfully"
