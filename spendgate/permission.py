import frappe

@frappe.whitelist()
def share_expense_claim(claim_name,user_email):
    frappe.share.add(
        "Expense Claim",
        claim_name,
        claim_email,
        read=1
    )

def expense_claim(user):
    roles=frappe.get_roles(user)
    if "SG Finance Manager" in roles:
        return ""

    if 