import frappe

def after_install():
    departments = ["Marketing","Travel & Client Entertainment","Equipment & Software","Training"]
    for dept in departments:
        if not frappe.db.exists("Department", dept):
            doc = frappe.get_doc({
                "doctype": "Department",
                "department_name": dept
            })
            doc.insert()
        
    categories=["Travel","Software & Equipment","Client Entertainment","Training"]
    for category in categories:
        if not frappe.db.exists("Expense Category", category):
            doc = frappe.get_doc({
                "doctype": "Expense Category",
                "category_name": category,
                "requires_receipt": 1
            })
            doc.insert()

    if not frappe.db.exists("SpendGate Settings", "SpendGate Settings"):
        doc = frappe.get_doc({
            "doctype": "SpendGate Settings",
            "finance_email": "logeshwarks2005@gmail.com",
            "low_budget_alert_threshold_percent": 90,
            "fiscal_year_start_month": 1
        })
        doc.insert()

    frappe.msgprint("SpendGate installed successfully")