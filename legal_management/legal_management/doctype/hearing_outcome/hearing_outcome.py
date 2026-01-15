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

        if getdate(hearing.hearing_date) > getdate(today()):
            frappe.throw(
                f"Hearing Outcome can only be created after the hearing date "
                f"({hearing.hearing_date})."
            )

    def before_submit(self):
        self.create_next_hearing_if_adjourned()

    def create_next_hearing_if_adjourned(self):
        if self.outcome_type != "Adjourned":
            return

        hearing = frappe.get_doc("Hearing", self.hearing)

        # ✅ next hearing date comes from Hearing
        if not hearing.next_hearing_date:
            frappe.throw("Next Hearing Date must be set in Hearing before adjournment.")

        # Prevent duplicates
        if frappe.db.exists(
            "Hearing",
            {
                "case": hearing.case,
                "hearing_date": getdate(hearing.next_hearing_date),
            }
        ):
            return

        # Create next hearing
        frappe.get_doc({
            "doctype": "Hearing",
            "case": hearing.case,
            "hearing_date": hearing.next_hearing_date,
            "court": hearing.court,
            "purpose": hearing.purpose,
            "assigned_lawyer": hearing.assigned_lawyer,
            "status": "Active"
        }).insert(ignore_permissions=True)
