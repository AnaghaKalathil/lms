import frappe

def apply_frontend_template(doc, method):
    """
    Apply frontend-built Email Template HTML to outgoing email
    """

    campaign = frappe.get_doc("Campaign", doc.campaign_name)

   
    if not campaign.campaign_schedules:
        frappe.throw("No Campaign Schedule found")

    
    template_name = campaign.campaign_schedules[0].email_template
    if not template_name:
        return

   
    template = frappe.get_doc("Email Template", template_name)

    
    if not template.response_html:
        frappe.throw("Selected Email Template has no HTML content")

   
    if not template.get("from_builder"):
        return

    
    doc.message = template.response_html

   
