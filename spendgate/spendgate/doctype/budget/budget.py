# Copyright (c) 2026, logeshwar and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class Budget(Document):
	def validate(self):
		if self.total_allocated<=0:
			frappe.throw("Total allocated must be greater then 0")

	def before_insert(self):
		if frappe.db.exists({
			"doctype":"Budget",
			"department":self.department,
			"fiscal_year":self.fiscal_year,
			"fiscal_quarter":self.fiscal_quarter,
			"name":("!=",self.name)
		}):
			frappe.throw("No duplicate budget allowed")