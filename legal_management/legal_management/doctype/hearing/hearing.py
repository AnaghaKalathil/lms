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
