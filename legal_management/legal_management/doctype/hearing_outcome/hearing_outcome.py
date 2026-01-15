import frappe
from frappe.model.document import Document
from frappe.utils import getdate, today


class HearingOutcome(Document):

    def validate(self):
        self.validate_hearing_date()

    def validate_hearing_date(self):
        if not self.hearing:
            return

        hearing = frappe.get_doc("Hearing", self.hearing)

        if not hearing.hearing_date:
            frappe.throw("Hearing date is not set.")

        # Block future hearings
        if getdate(hearing.hearing_date) > getdate(today()):
            frappe.throw(
                f"Hearing Outcome can only be created after the hearing date "
                f"({hearing.hearing_date})."
            )

    def before_submit(self):
        self.create_next_hearing_if_adjourned()

    def create_next_hearing_if_adjourned(self):
        # Only for adjournments
        if self.outcome_type != "Adjourned":
            return

        # ✅ next hearing date MUST come from Hearing Outcome
        if not self.next_hearing_date:
            frappe.throw("Next Hearing Date is required for Adjourned outcomes.")

        hearing = frappe.get_doc("Hearing", self.hearing)
        frappe.throw("I m here.")
        # Prevent duplicate next hearings
        if frappe.db.exists(
            "Hearing",
            {
                "case": hearing.case,
                "hearing_date": getdate(self.next_hearing_date),
            }
        ):
            return

        # Create next hearing
        frappe.get_doc({
            "doctype": "Hearing",
            "case": hearing.case,
            "hearing_date": self.next_hearing_date,
            "court": hearing.court,
            "purpose": hearing.purpose,
            "assigned_lawyer": hearing.assigned_lawyer,
            "status": "Active"
        }).insert(ignore_permissions=True)
