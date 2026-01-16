import frappe
from frappe.utils.password import update_password

@frappe.whitelist(allow_guest=True)
def register_customer(full_name, email, mobile, password):
    if frappe.db.exists("User", email):
        frappe.throw("User already exists")

    user = frappe.get_doc({
        "doctype": "User",
        "email": email,
        "first_name": full_name,
        "enabled": 1,
        "send_welcome_email": 0,
        "roles": [{"role": "Customer"}]
    })
    user.insert(ignore_permissions=True)

    update_password(email, password)

   
    # frappe.get_doc({
    #     "doctype": "Customer",
    #     "user": email,
    #     "mobile": mobile
    # }).insert(ignore_permissions=True)

    frappe.local.login_manager.authenticate(email, password)
    frappe.local.login_manager.post_login()

    return {"status": "success"}

@frappe.whitelist()
def create_case_interest(case_request):
    if "Lawyer" not in frappe.get_roles():
        frappe.throw("Only lawyers can express interest")

    if frappe.db.exists("Case Interest", {
        "case_request": case_request,
        "lawyer": frappe.session.user
    }):
        frappe.throw("Already interested")

    frappe.get_doc({
        "doctype": "Case Interest",
        "case_request": case_request,
        "lawyer": frappe.session.user,
        "status": "Interested"
    }).insert()

    return {"status": "success"}

@frappe.whitelist()
def create_case(case_interest):
    user = frappe.session.user

    # Allow only customers
    if "Customer" not in frappe.get_roles(user):
        frappe.throw("Only customers can accept a case")

    # Fetch Case Interest
    interest = frappe.get_doc("Case Interest", case_interest)

    case_request = interest.case_request
    assigned_lawyer = interest.lawyer

    # Ensure this case belongs to the customer
    case_owner = frappe.db.get_value("Case Request", case_request, "owner")
    if case_owner != user:
        frappe.throw("Not permitted")

    # Prevent duplicate Case
    if frappe.db.exists("Case", {"source_case_request": case_request}):
        frappe.throw("Case already created")

    # Create Case
    case = frappe.get_doc({
        "doctype": "Case",
        "case_title": case_request,
        "client": user,
        "assigned_lawyer": assigned_lawyer,
        "source_case_request": case_request,
        "status": "Active"
    }).insert(ignore_permissions=True)

    # Update Case Interest statuses
    frappe.db.sql("""
        UPDATE `tabCase Interest`
        SET status = 'Rejected'
        WHERE case_request = %s
    """, case_request)

    interest.db_set("status", "Accepted")

    # Update Case Request
    frappe.db.set_value(
        "Case Request",
        case_request,
        "status",
        "Accepted"
    )

    return {
        "status": "success",
        "case": case.name
    }

