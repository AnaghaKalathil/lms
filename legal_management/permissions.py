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

    
     # Customer view (ONLY own case requests)

    if "Customer" in roles:
        return (
            "`tabCase Request`.owner = {user}"
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
    # Customer view (ONLY own cases)

    if "Customer" in roles:
        return (
        "`tabCase`.client IN ("
        "SELECT name FROM `tabClient` "
        "WHERE client_name = {user}"
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

def caseinterest_permission_query(user):
    if user == "Administrator":
        return ""

    if "Lawyer" in frappe.get_roles(user):
        return (
            "("
            "`tabCase Interest`.lawyer = {user}"
            "AND "
            "`tabCase Interest`.status = 'Interested'"
            ")"
        ).format(user=frappe.db.escape(user))

     # Customers: see interests for their own case requests
    if "Customer" in frappe.get_roles(user):
        return (
            "`tabCase Interest`.case_request IN ("
            "SELECT name FROM `tabCase Request` "
            "WHERE owner = {user}"
            ")"
        ).format(user=frappe.db.escape(user))   # return "`tabCase Interest`.lawyer = %s" % frappe.db.escape(user)

    # Other users see nothing
    return "1=0"


