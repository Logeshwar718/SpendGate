# Copyright (c) 2026, logeshwar and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class ExpenseClaim(Document):
	def validate(self):
		for row in self.expense_lines:
			if row.amount<=0:
				frappe.throw("Amount should be greater than 0")

		total=0
		for row in self.expense_lines:
			total=total+row.amount
		self.total_amount=total

		bud_dept=frappe.db.get_value("Budget",self.budget,"department")
		if bud_dept!=self.department:
			frappe.throw("The chosen budget is from another department")

	def before_submit(self):
		budget=frappe.get_doc("Budget",self.budget)
		spent_so_far = frappe.db.sql("""SELECT COALESCE(SUM(total_amount), 0) FROM `tabExpense Claim` WHERE budget = %s AND docstatus = 1 AND name != %s""", (self.budget, self.name or ""))[0][0]
		total=spent_so_far+self.total_amount

		if total>budget.total_allocated:
			overage=total-budget.total_allocated
			remaining=budget.total_allocated-spent_so_far
			frappe.throw(
				f"Budget exceeded for department {budget.department}. Overage amount: {overage:.2f}. Budget remaining: {remaining:.2f}."
        	)
		
	def on_submit(self):
		budget=frappe.get_doc("Budget",self.budget)
		spent_so_far = frappe.db.sql("""SELECT COALESCE(SUM(total_amount), 0) FROM `tabExpense Claim` WHERE budget = %s AND docstatus = 1 AND name != %s""", (self.budget, self.name or ""))[0][0]
		remaining=budget.total_allocated-spent_so_far

		self.remaining_budget_at_submission=remaining

		if not self.approved_by:
			self.approved_by=frappe.session.user

		self.db_set("remaining_budget_at_submission",remaining)
		self.db_set("approved_by",self.approved_by)

	def on_cancel(self):
		if self.status=="Reimbursed":
			frappe.throw("Unable to cancel because the status is reimbursed")
		self.status="Cancelled"
		self.db_set("status",self.status)

	def on_trash(self):
		if self.status not in ["Cancelled","Draft"]:
			frappe.throw("Status with cancelled or draft only be deleted")
