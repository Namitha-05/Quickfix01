# B1  Trace a Request End-to-End 

-----> URL: /api/method/quickfix.api.get_job_summary
Which Python function handles- 
--
--This URL calls a custom Python function called get_job_summary inside the QuickFix app.
--Function: quickfix/api.py -> get_job_summary()
-- It must be whitelisted using @frappe.whitelist() to allow API access or browser.

How frappe finds it- Frappe sees the URL starts with /api/method/ -> identifies that it is a custom Python function call.
-- Then it extracts the dotted path: quickfix.api.get_job_summary.
-- Dynamically imports the module quickfix.api.
-- Calls the function get_job_summary().
-- Returns the available result as JSON to the browser.


-----> URL: /api/resource/Job Card/JC-2024-0001

- This URL uses Frappe's built-in REST API for DocTypes and it is not used for custom function.
- Frappe sees the URL starts with /api/resource/ -> identifies it as a DocType's record request.
- Internally, it calls: frappe.get_doc("Job Card", "JC-2024-0001").
- It performs:
  1. Permission check
  2. Fetches the document from database
  3. Returns the document as JSON to the browser

Difference from /api/method/:
- /api/method/ calls a custom Python function 
- /api/resource/ calls Frappe's built-in DocType API
- No whitelist is needed for /api/resource/ because it is standard CRUD
-/api/resource/Job Card/....is already handled by Frappe automatically.

Frappe already has built-in Python code to:
-Read the records
-Check permissions
-Return the JSON

-----> When a browser hits /track-job, Frappe looks in the app’s www/ folder and serves track-job.py or track-job.html.  
It uses the get_context function (if .py) or the HTML directly, because URLs not starting with /api/ are treated as website pages.


2) Session & CSRF
• X-Frappe-CSRF-Token:
It is a secret token created during login by the Frappe Framework and stored in your session to verify that the POST request is genuine; if omitted, Frappe blocks the request with a 403 error.

• frappe.session.data:
It contains details of the currently logged-in user like username, roles, session expiry, and CSRF token, which frappe uses to identify and authorize the user.


3) Error visibility :

• With the developer_mode: 1
When an error happens, the browser shows the full error details and traceback (file name and line number). This helps developers understand and fix the issue.

• With the developer_mode: 0

The browser shows only a simple message like “Something went wrong” and hides technical details. This is important in production to keep the system secure.

• Where do production errors go:

The full error details are saved in the Error Log inside Frappe Framework and in server log files for developers to check.

4) Permission check location:

If we call frappe.get_doc("Job Card", name) without ignore_permissions and log in as a Technician who was not assigned to that Job Card, Frappe raises a PermissionError (Not Permitted).

Frappe stops the request at the permission checking layer (before returning the document), so the user cannot access the data they are not allowed to see.


# C1 -Child Table Internals 

1.Frappe automatically sets parent, parenttype, parentfield, and idx when a child row is saved.

2.The DB table name is `tabPart Usage Entry`.

3.If idx = 2 is deleted and saved, Frappe automatically reorders and renumbers idx sequentially.


# C3 - Renaming task

1.After selecting a assigned-technician in job card. I have renamed it in the technician document. The changes had updated in the job card record. 
This happened because assigned_technician is a Link field and in Frappe, Link fields store the actual document name (primary key). When we rename a document properly using the Rename feature, Frappe automatically updates all the Link fields that were pointing to the old name which ensures data consistency and avoids broken links.

In track changes, the name changes was displayed as Administrator renamed from TECH-00001 to TECH-00002 .

2. unique field - strong rule enforced by the database.
frappe.db.exists() in validate - Custom check written in code.

