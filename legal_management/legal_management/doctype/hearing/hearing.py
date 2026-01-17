import frappe
from frappe.model.document import Document


class Hearing(Document):

    def after_insert(self):
        self.add_to_case_child_table()

    def add_to_case_child_table(self):
        if not self.case:
            return

        case = frappe.get_doc("Case", self.case)

        # prevent duplicates
        existing = {row.hearing for row in case.hearing}
        if self.name in existing:
            return

        case.append("hearing", {
            "hearing": self.name,
            "hearing_date": self.hearing_date,
            "status": self.status
        })

        case.save(ignore_permissions=True)

    def after_insert(self):
        self.notify_customer()

    def notify_customer(self):
        if not self.case:
            return

        case = frappe.get_doc("Case", self.case)

        if not case.source_case_request:
            return

        case_request = frappe.get_doc("Case Request", case.source_case_request)

        if not case_request.email:
            return

    # Ensure user exists
        if not frappe.db.exists("User", case_request.email):
            return

        frappe.publish_realtime(
        event="notification",
        message={
            "title": "New Hearing Scheduled",
            "description": f"Hearing on {self.hearing_date} for case {case.case_title}",
            "doctype": "Hearing",
            "docname": self.name,
        },
        user=case_request.email
        )


