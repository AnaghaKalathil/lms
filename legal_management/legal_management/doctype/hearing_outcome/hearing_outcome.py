import frappe
from frappe.model.document import Document
from frappe.utils import getdate, today


class HearingOutcome(Document):

    def on_submit(self):
        case = frappe.get_doc("Case", self.case)
        cr = frappe.get_doc("Case Request", case.source_case_request)
        hearing = frappe.get_doc("Hearing", self.hearing)

        user = None

        if getattr(cr, "linked_user", None):
            user = cr.linked_user
        elif frappe.db.exists("User", cr.email):
            user = cr.email
        else:
            return

        frappe.get_doc({
        "doctype": "Notification Log",
        "subject": "Hearing Outcome Update",
        "email_content": (
            f"Your case <b>{hearing.case}</b> hearing on "
            f"<b>{hearing.hearing_date}</b> has been "
            f"<b>{self.outcome_type}</b> at <b>{hearing.court}</b>."
            f"<b>  Contact your lawyer for more details..</b>."
        ),
        "type": "Alert",
        "for_user": user,
        "document_type": "Hearing Outcome",
        "document_name": self.name
    }).insert(ignore_permissions=True)



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
