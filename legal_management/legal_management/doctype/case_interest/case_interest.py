import frappe
from frappe.model.document import Document

class CaseInterest(Document):

    def validate(self):
        self.validate_duplicate_interest()
        self.validate_lawyer_role()

    def validate_duplicate_interest(self):
        if frappe.db.exists("Case Interest", {
            "case_request": self.case_request,
            "lawyer": self.lawyer,
            "name": ["!=", self.name]
        }):
            frappe.throw("You have already expressed interest in this case")

    def validate_lawyer_role(self):
        if "Lawyer" not in frappe.get_roles(self.lawyer):
            frappe.throw("Only lawyers can express interest")
