import frappe

def case_request_permission_query(user):
    if user == "Administrator":
        return ""

    roles = frappe.get_roles(user)
    if "Lawyer" in roles:
        return (
            "("
            "`tabCase Request`.status != 'Accepted' "
            "OR "
            "`tabCase Request`.assigned_lawyer = {user}"
            ")"
        ).format(user=frappe.db.escape(user))

    return ""

def case_permission_query(user):
    if user == "Administrator":
        return ""

    roles = frappe.get_roles(user)
    if "Lawyer" in roles:
        return (
            "("
            "`tabCase`.assigned_lawyer = {user}"
            "AND "
            "`tabCase`.status = 'Active'"
            ")"
        ).format(user=frappe.db.escape(user))

    return ""

def client_permission_query(user):
    if user == "Administrator":
        return ""

    roles = frappe.get_roles(user)
    if "Lawyer" in roles:
        return (
            "("
            "`tabClient`.assigned_lawyer = {user}"
            "AND "
            "`tabClient`.status = 'Active'"
            ")"
        ).format(user=frappe.db.escape(user))

    return ""

def hearing_permission_query(user):
    if user == "Administrator":
        return ""

    if "Lawyer" in frappe.get_roles(user):
        return "`tabHearing`.assigned_lawyer = %s" % frappe.db.escape(user)

    # Other users see nothing
    return "1=0"


