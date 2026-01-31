import frappe


def send_email_campaign_now(campaign_name):
    """
    Send an Email Campaign immediately to all members of its linked Email Group.
    """

    campaign = frappe.get_doc("Email Campaign", campaign_name)

    # Get Email Group
    email_group_name = campaign.recipient or campaign.email_group
    if not email_group_name:
        frappe.log_error(
            f"No Email Group linked to campaign {campaign_name}",
            "Campaign Send"
        )
        return

    # Fetch subscribers
    subscribers = frappe.get_all(
        "Email Group Member",
        filters={"email_group": email_group_name},
        pluck="email"
    )

    if not subscribers:
        frappe.log_error(
            f"No subscribers in Email Group {email_group_name}",
            "Campaign Send"
        )
        return

    subject = campaign.campaign_name
    message = "Hello, this is a test email from your campaign."

    for email in subscribers:
        try:
            frappe.sendmail(
                recipients=email,
                sender=campaign.sender or None,
                subject=subject,
                message=message,
                reference_doctype="Email Campaign",
                reference_name=campaign.name,
                now=True
            )
        except Exception as e:
            frappe.log_error(str(e), "Campaign Send Failed")

    # Mark campaign as sent
    frappe.db.set_value("Email Campaign", campaign.name, "status", "Sent")
    frappe.db.commit()


def on_submit(doc, method):
    """
    Triggered when Campaign Email Schedule is submitted
    """
    if not doc.parent:
        return

    send_email_campaign_now(doc.parent)
