import json
import frappe

def refresh_email_group_segment(email_group_name):
    ALLOWED_FIELDS = {"email", "unsubscribed", "full_name", "first_name", "last_name"}
    ALLOWED_OPERATORS = {"=", "!=", "LIKE", "NOT LIKE", "IN", "NOT IN"}

    group = frappe.get_doc("Email Group", email_group_name)

    if not group.segment_rules or not group.source_email_group:
        return set()

    segment = json.loads(group.segment_rules)
    conditions = segment.get("conditions", [])

    if not conditions:
        return set()

    where_clauses = []
    params = {"source_group": group.source_email_group}

    for i, c in enumerate(conditions):
        field = c.get("field")
        op = c.get("condition") or "="
        value = c.get("value")

        if field not in ALLOWED_FIELDS or op not in ALLOWED_OPERATORS:
            continue

        key = f"val_{i}"

        if op in ("IN", "NOT IN"):
            if not isinstance(value, list):
                value = [v.strip() for v in str(value).split(",") if v.strip()]

            placeholders = []
            for j, v in enumerate(value):
                pname = f"{key}_{j}"
                placeholders.append(f"%({pname})s")
                params[pname] = v

            where_clauses.append(f"`{field}` {op} ({', '.join(placeholders)})")

        elif op in ("LIKE", "NOT LIKE"):
            where_clauses.append(f"`{field}` {op} %({key})s")
            params[key] = f"%{value}%"

        elif op == "!=" and (value is None or value == ""):
            where_clauses.append(f"`{field}` IS NOT NULL AND `{field}` != ''")

        else:
            where_clauses.append(f"`{field}` {op} %({key})s")
            params[key] = value

    where_sql = " AND ".join(where_clauses) or "1=1"

    rows = frappe.db.sql(
        f"""
        SELECT DISTINCT email
        FROM `tabEmail Group Member`
        WHERE email_group = %(source_group)s
          AND email IS NOT NULL
          AND email != ''
          AND {where_sql}
        """,
        params,
        as_dict=True
    )

    return {r["email"] for r in rows}
def sync_segment_email_group(email_group_name):
    group = frappe.get_doc("Email Group", email_group_name)

    if not group.segment_rules or not group.source_email_group:
        return 0

    target_emails = refresh_email_group_segment(email_group_name)

    existing_emails = set(
        frappe.db.get_all(
            "Email Group Member",
            filters={"email_group": email_group_name},
            pluck="email"
        )
    )

    to_add = target_emails - existing_emails
    to_remove = existing_emails - target_emails

    if to_remove:
        frappe.db.sql(
            """
            DELETE FROM `tabEmail Group Member`
            WHERE email_group = %(g)s
              AND email IN %(emails)s
            """,
            {"g": email_group_name, "emails": tuple(to_remove)}
        )

    if to_add:
        frappe.db.bulk_insert(
            "Email Group Member",
            ["name", "email_group", "email", "unsubscribed"],
            [
                (frappe.generate_hash(length=10), email_group_name, email, 0)
                for email in to_add
            ]
        )

    # ✅ FIX: update subscriber count
    count = frappe.db.count(
        "Email Group Member",
        filters={"email_group": email_group_name}
    )

    frappe.db.set_value(
        "Email Group",
        email_group_name,
        "total_subscribers",
        count,
        update_modified=False
    )

    frappe.db.commit()
    return count


def on_member_change(doc, method=None):
    """
    Automatically sync segmented Email Groups when created or updated
    """
    if doc.segment_rules and doc.source_email_group:
        sync_segment_email_group(doc.name)
