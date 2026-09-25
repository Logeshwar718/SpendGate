# B2c — Dangerous Patterns
Given code:
def validate(self):
    self.total_amount = sum(r.amount for r in self.expense_lines)
    self.save()
    budget = frappe.get_doc("Budget", self.budget)
    budget.total_allocated -= self.total_amount
    budget.save()

Corrected code:
def validate(self):
    self.total_amount = sum(r.amount for r in self.expense_lines)

self.save() should not called inside the validate function, because validate() is called once we save the document.
total_allocated should not change, it should contain the original budget.

# B2d — The Race Condition Question
Both submissions will succeed even if the sum of both their budget exceeds the total_allocated budget. If both transactions calculate the spent_so_far, they both see the same old budget_remaining value. For this we need to write an concurrency control mechanism like database row lock strategy.

# C3 — Expense Line
If the department name is changed,its linked budget field in the expense claim doctype will not automatically change the value in the department field in the expense claim doctype. Link fields store the linked document name, so changing the department name requires the linked references to be updated.

# D2 — Row-Level Filtering & Data Leaks
frappe.get_all() - gives all the data without filtering permissions.
frappe.get_list() - gives the data with permission filters.
frappe.db.get_all() is dangerous in a public/whitelisted method because the user call the API directly and receive the data.

# E1 — Complete Lifecycle
Calling self.save() inside on_update() is wrong because save() triggers on_update() again. This creates a loop where on_update() keeps calling save() repeatedly and can cause a recursion error.
Instead we can update the required fields inside on_update() without calling self.save() again.

# H1 — Expense Claim Form Script
frappe.call() takes some time to get the answer from the server. But validate needs the answer immediately before the form is saved. So the result may come too late.
That is why we fetch the data in onload or refresh first, and then use the fetched data when validate runs.

# I1 — Query Report: Pending Approvals
f-string version:
f"select name,employee,department,total_amount,expense_date from `tabExpense Claim` where status='Pending Approval' and department='{department}'"

parameterized version:
select name,employee,department,total_amount,expense_date from `tabExpense Claim` where status='Pending Approval' and department=%(department)s;

The parameterized version is preferred because the value is passed separately from the SQL query.

# J1 — Expense Claim Voucher
Putting frappe.get_all() directly inside the Jinja template makes the print format do database work while generating the HTML.
A better approach is to fetch the required data in before_print() and store it in a field such as doc.precomputed_field.

# L1 — Custom Whitelisted Method
Test the standard /api/resource/Expense Claim CRUD once with curl and document one request/response pair.
Curl command: curl -X GET "http://127.0.0.1:8000/api/resource/Expense%20Claim/EXP-2026-00004" -H "Authorization: token b24b99473c4ea87:820a37d406679bf"
Output: {"data":{"name":"EXP-2026-00004","owner":"Administrator","creation":"2026-09-25 14:10:59.958115","modified":"2026-09-25 14:28:58.396487","modified_by":"Administrator","docstatus":1,"idx":0,"employee":"logeshwar64@gmail.com","department":"Travel & Client Entertainment","budget":"BUD-2026-0015","expense_date":"2026-09-25","description":"Trip to manali","total_amount":50000.0,"remaining_budget_at_submission":100000.0,"status":"Pending Approval","approved_by":"Administrator","doctype":"Expense Claim","expense_lines":[{"name":"10ntb7ldpf","owner":"Administrator","creation":"2026-09-25 14:10:59.958115","modified":"2026-09-25 14:28:58.396487","modified_by":"Administrator","docstatus":1,"idx":1,"category":"Travel","vendor":"VEND-0001","amount":50000.0,"parent":"EXP-2026-00004","parentfield":"expense_lines","parenttype":"Expense Claim","doctype":"Expense Line"}]}}