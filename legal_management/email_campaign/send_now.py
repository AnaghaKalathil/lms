import frappe

@frappe.whitelist()
def send_campaign_now(campaign_name):
    campaign = frappe.get_doc("Email Campaign", campaign_name)
    campaign.reload()

    template_name = campaign.get("custom_email_template")
    if not template_name:
        frappe.throw("Please select and save an Email Template before sending")

    template = frappe.get_doc("Email Template", template_name)

    subject = template.subject or campaign.campaign_name
    html = template.response_html

    # Build recipients
    recipients = []
    if campaign.email_campaign_for == "Email Group":
        if not campaign.recipient:
            frappe.throw("Please select an Email Group")
        recipients = frappe.get_all(
            "Email Group Member",
            filters={"email_group": campaign.recipient, "unsubscribed": 0, "email": ["!=", ""]},
            pluck="email"
        )
    elif campaign.email_campaign_for == "Lead":
        recipients = frappe.get_all(
            "Lead",
            filters={"email_id": ["!=", ""]},
            pluck="email_id"
        )
    else:
        frappe.throw("Unsupported campaign type")

    if not recipients:
        frappe.throw("No recipients found")

    # Send emails
    for email in recipients:
        frappe.sendmail(
            recipients=email,
            subject=subject,
            message=html,
            sender=campaign.sender,
            reference_doctype="Email Campaign",
            reference_name=campaign.name,
            now=True
              
        )

    campaign.status = "Completed"
    campaign.save(ignore_permissions=True)
    frappe.db.commit()

    return f"Campaign sent to {len(recipients)} recipients"
