import frappe
from frappe.email.doctype.newsletter.newsletter import Newsletter

class CustomNewsletter(Newsletter):

    def queue_email(self, email, unsubscribe_url=None):
        email_args = self.get_email_args(email, unsubscribe_url)
        frappe.sendmail(
            recipients=email,
            subject=self.subject,
            content=self.get_content(unsubscribe_url),
            reference_doctype=self.doctype,
            reference_name=self.name,
            unsubscribe_message=self.get_unsubscribe_message(email),
            now=True
        )

    def send(self):
       
        self.validate()
        self.set_email_sent()
        self.send_emails()
