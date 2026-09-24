import frappe
from frappe.query_builder import DocType

@frappe.whitelist()
def budget_status(budget_name):
    budget=frappe.db.get_value("Budget",budget_name,["total_allocated"],as_dict=True)
    spent=frappe.db.sql("""
    SELECT COALESCE(SUM(total_amount), 0) FROM `tabExpense Claim`
    WHERE budget = %s AND docstatus = 1""",
    budget_name)[0][0]
    remaining=budget.total_allocated-spent
    return{
        "allocated":budget.total_allocated,
        "spent":spent,
        "remaining":remaining
    }

@frappe.whitelist()
def reassign_department(claim_name, department):
    frappe.db.set_value(
        "Expense Claim",
        claim_name,
        "department",
        department
    )

@frappe.whitelist()
def get_claims_pending_approval():
    ec=DocType("Expense Claim")
    result=(frappe.qb.from_(ec).select(ec.name,ec.employee,ec.department,ec.total_amount,ec.expense_date).where(ec.status=="Pending Approval").orderby(ec.expense_date).run(as_dict=True))
    return result

@frappe.whitelist()
def reassign_department_claims(from_dept, to_dept):
    try:
        frappe.db.sql("""update `tabExpense Claim` set department=%s where department=%s and docstatus=0""",(to_dept,from_dept))
        frappe.db.commit()
    except Exception:
        frappe.db.rollback()
        frappe.log_error(frappe.get_traceback(),"Failed to reassign")
        raise

