import frappe
from frappe.core.doctype.communication.email import make

@frappe.whitelist()
def send_campaign_now(campaign_name):
    campaign = frappe.get_doc("Email Campaign", campaign_name)

    # 🔴 Ensure MJML is compiled
    if not campaign.html_content:
        frappe.throw("Please compile MJML before sending")

    recipients = []

    # 🔹 Email Group
    if campaign.email_campaign_for == "Email Group":

        if not campaign.recipient:
            frappe.throw("Email Group not selected")

        recipients = frappe.get_all(
            "Email Group Member",
            filters={
                "email_group": campaign.recipient,
                "unsubscribed": 0
            },
            pluck="email"
        )

    # 🔹 Lead
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

    sent = 0

    for email in recipients:
        make(
            recipients=email,
            subject=campaign.campaign_name,
            content=campaign.html_content,
            communication_type="Communication",
            send_email=True,
            enqueue=True,
            now=True
        )
        sent += 1

    frappe.db.commit()

    return f"Campaign sent to {sent} recipients"
