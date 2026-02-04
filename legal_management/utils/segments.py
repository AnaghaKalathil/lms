import json
import frappe
from frappe.utils import now

def refresh_email_group_segment(email_group_name):
    ALLOWED_FIELDS = {"email", "unsubscribed", "full_name", "first_name", "last_name"}
    ALLOWED_OPERATORS = {"=", "!=", "LIKE", "NOT LIKE", "IN", "NOT IN"}

    group = frappe.get_doc("Email Group", email_group_name)

    if not group.segment_rules or not group.source_email_group:
        return []

    segment = json.loads(group.segment_rules)
    conditions = segment.get("conditions", [])

    if not conditions:
        return []

    where_clauses = []
    params = {"source_group": group.source_email_group}

    for i, c in enumerate(conditions):
        field = c.get("field")
        op = c.get("condition") or "="
        value = c.get("value")

        if field not in ALLOWED_FIELDS:
            continue
        if op not in ALLOWED_OPERATORS:
            continue

        key = f"val_{i}"

        if op in ("IN", "NOT IN"):
            if not isinstance(value, list):
                value = [v.strip() for v in str(value).split(",")]
            placeholders = ", ".join([f"%({key}_{j})s" for j in range(len(value))])
            where_clauses.append(f"`{field}` {op} ({placeholders})")
            for j, v in enumerate(value):
                params[f"{key}_{j}"] = v
        elif op in ("LIKE", "NOT LIKE"):
            where_clauses.append(f"`{field}` {op} %({key})s")
            params[key] = f"%{value}%"
        elif op == "!=" and (value is None or value == ""):
            where_clauses.append(f"`{field}` IS NOT NULL AND `{field}` != ''")
        else:
            where_clauses.append(f"`{field}` {op} %({key})s")
            params[key] = value

    where_sql = " AND ".join(where_clauses) or "1=1"

    members = frappe.db.sql(
        f"""
        SELECT email, name
        FROM `tabEmail Group Member`
        WHERE email_group = %(source_group)s
          AND email IS NOT NULL
          AND email != ''
          AND {where_sql}
        """,
        params,
        as_dict=True
    )

    return members

def sync_segment_email_group(email_group_name):
    group = frappe.get_doc("Email Group", email_group_name)

    if not group.segment_rules or not group.source_email_group:
        return 0

    members = refresh_email_group_segment(email_group_name)

    # Delete existing members
    frappe.db.sql(
        "DELETE FROM `tabEmail Group Member` WHERE email_group = %(g)s",
        {"g": email_group_name}
    )

    # Insert new members
    for m in members:
        frappe.get_doc({
            "doctype": "Email Group Member",
            "email_group": email_group_name,
            "email": m["email"],
            "unsubscribed": 0
        }).insert(ignore_permissions=True)

    group.db_set("last_refreshed_on", now())
    frappe.db.commit()
    return len(members)

def on_member_change(doc, method=None):
    """
    Automatically sync segmented Email Groups when created or updated
    """
    if doc.segment_rules and doc.source_email_group:
        sync_segment_email_group(doc.name)