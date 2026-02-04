import frappe
from legal_management.utils.segments import refresh_email_group_segment

def on_update(doc, method=None):
    if not doc.segment_rules:
        return

    if not doc.source_email_group:
        return

    frappe.enqueue(
        method=refresh_email_group_segment,
        queue="short",
        group_name=doc.name
    )
