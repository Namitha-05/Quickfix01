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
frappe.db.exists() in validate - Custom check written in code.Less strict than Unique field.



# D1 -Roles and Permission matrix

->If a non-manager calls  the frappe.only_for("QF Manager") means Permission error is occuring.

-> frappe.permissions.get_doc_permissions(doc)
For set_user() as manager@gmail.com for job card,

{'if_owner': {},
 'has_if_owner_enabled': False,
 'select': 1,
 'read': 1,
 'write': 1,
 'create': 1,
 'delete': 1,
 'submit': 1,
 'cancel': 1,
 'amend': 1,
 'print': 1,
 'email': 1,
 'report': 1,
 'import': 0,
 'export': 1,
 'share': 1}


 # D2: Permission Query and has_permission:

 ->frappe.get_all() bypasses permission_query_conditions and record-level permissions.
 ->If exposed to guests or low-privilege users, it can return all records and leak sensitive data.

 ->Always use frappe.get_list() in APIs because it respects user  permissions and prevents data leaks.


 # E1 Job card lifecycle

 on_update() ->   recursion pitfall

 If self.save() is called inside on_update(), it creates infinite recursion because saving the document triggers validate() and on_update() again. This leads to repeated save cycles, eventually causing a maximum recursion depth error and potential server crash.
Therefore, lifecycle methods should not manually call save().


# E3- Part-B Upgrade friction analysis:
doc_events is safer than override_doctype_class because it adds custom logic on top of the existing DocType without replacing it. This ensures core validations and future updates always run.

override_doctype_class can break things if forget to call super().



# F1 - doc_events: Wildcard, Multiple Handlers, Order

Handler order in Frappe:
When both controller and doc_events define same method like validate method,
the execution order is:

1. Controller validate method runs first
2. doc_events handler runs next

If the controller raises frappe.ValidationError,
execution stops immediately and then the doc_events handler will not run.

If both controller and doc_events raise ValidationError,
only the first error is shown because Frappe stops at the first exception itself.

Wildcard vs specific DocType handler:

If both "*" and a specific DocType handler are registered
for the same event, both handlers will run.

Execution order is:
1. Controller method
2. Specific DocType handler
3. Wildcard handler

->Wildcard runs for all DocTypes, so it is executed after
the specific handler.


# F3 – Asset, Jinja & Website Hooks
# Asset Hooks

-->app_include_js vs web_include_js

->app_include_js loads JavaScript only in the Desk UI for logged-in users.
It is used when we want scripts to run inside forms, list views, or any page inside.

->web_include_js loads JavaScript only in Website pages.
It is used for public pages, guest users, or custom website routes.

Use app_include_js for desk features.
Use web_include_js for website features.

-->doctype_js for Job Card
doctype_js loads a JavaScript file only when a specific DocType form is opened.

-->doctype_list_js for Job Card
doctype_list_js loads JavaScript only in the list view of a DocType.

-->doctype_tree_js (not applicable)
doctype_tree_js is used for DocTypes that have hierarchical structure.
Tree view is used when records have parent-child relationship.Job Card does not have hierarchy, so tree view is not used.


-->Build cache-busting
-->Command:
 bench build --app quickfix
This command rebuilds frontend assets.

Frappe bundles files from public/js into /assets/quickfix/.

Browsers cache old JavaScript files.
After changing JS, the old file may still load.

Running bench build clears cache and loads the new file.
This is called cache-busting.

# Jinja hooks:

Difference Between Jinja Context in Print Formats and Web Pages

No, they are not same.

Print Format Jinja Context:
Automatically provides the current document as doc. It is directly tied to a specific DocType record and is mainly used for generating printable documents (PDF/HTML).

Web Page Jinja Context:
Does not automatically provide doc. Data must be passed manually using get_context(). It is used for public or portal web pages and is not restricted to a single document.



# F4 - override_whitelisted_methods Hook:

-->Difference Between override_whitelisted_methods and Monkey Patching:

override_whitelisted_methods is a Frappe hook defined in hooks.py that explicitly replaces a whitelisted method with a custom implementation. It is framework-supported, reversible, maintainable, and upgrade-safe.

Monkey patching directly reassigns a function at import time in Python. It is invisible, brittle, hard to debug, and not recommended for production.

Using override_whitelisted_methods for production-safe API overrides. Use monkey patching only for temporary debugging or testing.


-->What Happens If Two Apps Override the Same Method:

If two apps register override_whitelisted_methods for the same method, the app that is loaded last (based on sites/apps.txt) takes precedence. The earlier override is silently replaced. No warning is shown. Only one override will be active.

-->Signature Mismatch and TypeError:

When overriding a method, the custom function must match the original function's signature exactly.

If the number or names of parameters differs, the Python raises a TypeError when the method is called because the framework passes arguments based on the original signature.

Therefore, the override function must accept the same parameters as the original method to avoid runtime errors.


# F5 - Fixtures & Property Setters in Install 

->what happens if your Custom Field has the same
fieldname as a field added by a future Frappe update?

If a Custom Field uses the same fieldname as a field introduced later by a Frappe update, it creates a fieldname collision.

This can cause:
Migration failures
Database schema conflicts
Unexpected behavior in forms
App updates breaking

Frappe cannot have two fields with the same fieldname in the same DocType.
Therefore, always use unique, app-specific prefixes (e.g., qf_custom_status) to avoid future conflicts.

->Patch 1 creates a Custom Field and Patch 2 reads it, why
must they be separate entries in patches.txt and never merged?

Patches run one by one in the order they are written in patches.txt.If Patch 1 creates a Custom Field and Patch 2 tries to use that field, Patch 1 must run first.That is why, they should be written as separate entries.
If merged together, the second logic might run before the field is properly created, which can cause errors.Keeping patches separate ensures everything runs safely and in the correct order.



# H1 - Job Card Form Script
->Making a frappe.call inside the validate client event (before_save handler):

frappe.call is asynchronous, so the save process may continue before the server response is received. Because of this, the validation may not wait for the result and may cause unexpected behavior. Hence, using frappe.call in validate is not reliable.

->Using onload or refresh for async data fetches :

onload and refresh run when the form is loaded or refreshed, not during saving.
So we can safely use frappe.call to fetch data from the server asynchronously and update fields or UI without affecting the save process.