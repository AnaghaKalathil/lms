import frappe
from frappe.model.document import Document
import random

class CaseRequest(Document):

    def before_insert(self):
        self.set_user_email()

    def set_user_email(self):
        user = frappe.session.user

        # Only for logged-in users (not Guest)
        if user == "Guest":
            return

        roles = frappe.get_roles(user)

        if "Customer" in roles:
            self.email = user

    def autoname(self):
        self.name = self.generate_kl_number()

    def generate_kl_number(self):
        while True:
            number = "KL" + "".join([str(random.randint(0, 9)) for _ in range(10)])
            if not frappe.db.exists(self.doctype, number):
                return number
