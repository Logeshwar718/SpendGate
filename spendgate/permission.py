import frappe

@frappe.whitelist()
def share_expense_claim(claim_name,user_email):
    frappe.share.add(
        "Expense Claim",
        claim_name,
        user_email,
        read=1
    )

def expense_claim_query(user):
    roles=frappe.get_roles(user)
    if "SG Finance Manager" in roles:
        return ""
    if "SG Staff" in roles:
        return f"`tabExpense Claim`.`employee`={frappe.db.escape(user)}"
    if "SG Department Head" in roles:
        department=frappe.db.get_value(
            "Department",
            {"department_head": user},
            "name"
        )
        return f"`tabExpense Claim`.`department` = {frappe.db.escape(department)}"
    return "1=0" 