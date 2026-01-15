import frappe
from frappe.model.document import Document


class CaseRequest(Document):

    def on_update(self):
        self.create_case_on_accept()

    def create_case_on_accept(self):
        # run only when accepted
        if self.status != "Accepted":
            return

        # prevent duplicate cases
        if frappe.db.exists("Case", {"source_case_request": self.name}):
            return

        # create client
        client = frappe.get_doc({
            "doctype": "Client",
            "client_name": self.full_name,
            "email": self.email,
            "phone": self.phone,
            "assigned_lawyer": frappe.session.user,
            "status": "Active"
        }).insert(ignore_permissions=True)

        # create accepted case
        case = frappe.get_doc({
            "doctype": "Case",
            "case_title": f"{self.case_type} - {self.full_name}",
            "client": self.client,
            "assigned_lawyer": frappe.session.user,
            "case_type": self.case_type,
            "source_case_request": self.name,
            "status": "Active"
        }).insert(ignore_permissions=True)

        # update request
        self.client = client.name
        self.assigned_lawyer = frappe.session.user



