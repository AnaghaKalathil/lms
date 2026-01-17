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
    roles = frappe.get_roles(user)
    if "Customer" in roles:
        return (
            "`tabCase`.source_case_request IN ("
            "SELECT `name` FROM `tabCase Request` "
            "WHERE email = {user}"
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
    roles = frappe.get_roles(user)
    if "Customer" in roles:
        return """
            `tabHearing`.case IN (
                SELECT c.name
                FROM `tabCase` c
                JOIN `tabCase Request` cr
                    ON cr.name = c.source_case_request
                WHERE cr.email = {user}
            )
        """.format(user=frappe.db.escape(user))

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
    roles = frappe.get_roles(user)
    if "Customer" in roles:
        return (
            "`tabCase Interest`.case_request IN ("
            "SELECT `name` FROM `tabCase Request` "
            "WHERE email = {user}"
            ")"
        ).format(user=frappe.db.escape(user))
    
    return "1=0"

def hearingoutcome_permission_query(user):
    if user == "Administrator":
        return ""

    if "Lawyer" in frappe.get_roles(user):
        return "`tabHearing Outcome`.recorded_by = %s" % frappe.db.escape(user)
   
    roles = frappe.get_roles(user)

    if "Customer" in roles:
        return """
            `tabHearing Outcome`.hearing IN (
                SELECT h.name
                FROM `tabHearing` h
                JOIN `tabCase` c ON c.name = h.case
                JOIN `tabCase Request` cr ON cr.name = c.source_case_request
                WHERE cr.email = {user}
            )
        """.format(user=frappe.db.escape(user))
    
    return "1=0"


