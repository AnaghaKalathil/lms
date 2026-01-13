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
            "status": "Active"
        }).insert(ignore_permissions=True)

        # create accepted case
        case = frappe.get_doc({
            "doctype": "Case",
            "case_title": f"{self.case_type} - {self.full_name}",
            "client": client.name,
            "assigned_lawyer": frappe.session.user,
            "case_type": self.case_type,
            "source_case_request": self.name,
            "status": "Open"
        }).insert(ignore_permissions=True)

        # update request
        self.client = client.name
        self.assigned_lawyer = frappe.session.user


def get_permission_query_conditions(user):
   # if user == "Administrator":
      #  return ""*/

    # lawyers see ONLY new case requests
    return "`tabCase Request`.status = 'New'"
