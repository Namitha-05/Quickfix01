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


# H3 Tree View

what a Tree DocType?
 A Tree DocType is just records arranged in a parent → child structure. Like folders inside folders. Real examples: Account (Assets → Bank Account).


What is doctype_tree_js for?
It's the JavaScript file that customises the Tree View page — you use it to add custom buttons, handle node clicks, or control what shows in the tree. Without it, the tree still works; it's only needed for extra behaviour.

The 2 required extra fields:

parent_field -> a Link field pointing to the same DocType. Stores "who is my parent?" If empty, that record is the root.
is_group -> a Yes/No checkbox. If Yes, the node is a folder (can have children). If No, it's a leaf (no children allowed, actual working record).



# H4  Client Script DocType vs Shipped JS:
when would a consultant use Client Script DocType vs an app developer use shipped JS? 
Client Script DocType is mainly used by consultants for quick UI customizations directly from the system without changing the app code. It is easy to create and modify from the interface.

Shipped JS is used by app developers. The JavaScript is stored inside the app, tracked in Git, and deployed with the application, making it easier to maintain and manage.

What are the risks of Client Script DocType in production?

Client Scripts are not version controlled, so changes are hard to track. They may also be lost during migrations or site restores, and too many scripts can make the system hard to maintain and debug.
Therefore, important logic should be implemented in app-level JS instead of Client Scripts.

Why Hiding with JS is Not Secure?

Hiding fields with JavaScript only affects the user interface. The data still exists on the server, so it can be accessed through APIs or other requests.
Therefore, real security should be implemented using proper role permissions or server-side access control, not just by hiding fields in the UI.

# I1 Query Report with SQL Safety :

 f-string SQL vs Parameterized Query

# Problem with f-string SQL

f-string directly puts user input into the SQL query.
A malicious user can pass SQL code as input
and manipulate the query.

Unsafe example:
    device_type = "' OR '1'='1"
    query = f"SELECT * FROM `tabJob Card` 
              WHERE device_type = '{device_type}'"

The query becomes:
    WHERE device_type = '' OR '1'='1'

Since 1=1 is always true, this returns ALL records.
This is a SQL injection attack.

# Solution - Parameterized Query

    query = """SELECT * FROM `tabJob Card`
               WHERE device_type = %(device_type)s"""

    frappe.db.sql(query, {"device_type": device_type})

%(device_type)s is a placeholder.
Frappe escapes the value before inserting it.
Malicious input is treated as plain text - not SQL code.
Attack is blocked.

# Rule
Never use f-strings or string concatenation in SQL queries.
Always use %(fieldname)s placeholders with a values dict.


# EXPLAIN Statement

EXPLAIN shows how MySQL executes a query.
It tells you if MySQL is using an index or scanning every single row.

Before adding index:
    key: None  -> no index -> full table scan
    type: ALL  -> reading every row -> slow on large tables

After adding search_index: 1 to status field in DocType JSON
and running bench migrate:
    key: status -> index used → fast
    type: range -> only reading relevant rows

# Why Index Matters

Without index:
    100 Job Cards  -> reads 100 rows to find matches
    10000 Job Cards -> reads 10000 rows → very slow

With index:
    100 Job Cards  -> reads only matching rows
    10000 Job Cards -> still fast → index jumps to matches

# search_index: 1

Adding search_index: 1 to a field in DocType JSON
tells Frappe to create a MySQL index on that column.
Run bench migrate after adding it to create the index.


# I4 - Prepared Report 

when you would use a Prepared Report vs a
real-time Script Report?

A Script Report runs immediately when the user clicks "Run". The query executes in real time and returns results instantly. This is suitable for small or medium datasets where queries are fast.

A Prepared Report is used when the dataset is very large or the query is expensive. Instead of running immediately, the report is executed in a background worker using the job queue system. The result is computed and stored, and the user can download the prepared output later.

Prepared Reports improve system performance because they prevent long-running queries from blocking the user interface.

When to Use Prepared Reports

Prepared Reports should be used when:

• The report processes large datasets
• The query takes several seconds or minutes
• Many users may run the report simultaneously
• The report does heavy aggregation or calculations


Staleness Tradeoff

Prepared Reports introduce a data freshness tradeoff.

Because the report result is pre-computed and cached, the data may become stale if the underlying records change.

Example:

9:00 AM → Prepared report generated
9:05 AM → New Job Card added
9:10 AM → User downloads report

The report will not include the new Job Card, because the result was generated earlier.

Caching Risk

If the underlying data changes between report preparations, the user will see old cached results instead of real-time data.

This means:
• Recently updated Job Cards may not appear
• Status changes may not be reflected
• Counts may be outdated

To reduce this issue, the report must be re-run periodically or manually refreshed.


->When is Report Builder appropriate?
Report Builder is suitable for simple reports where users only need basic filtering, sorting, and viewing data from a single DocType without writing code.

->When must you use Script Report?
Script Reports are required when the report needs complex logic, SQL queries, joins between multiple DocTypes, or calculations that cannot be handled by Report Builder.

->Scenario where using Report Builder in production would be a mistake
Using Report Builder for a large or complex report, such as a Technician Performance report analyzing thousands of Job Cards, would be a mistake. It may cause slow queries and poor system performance, whereas a Script Report allows optimized queries and better control over the logic.





## Multi-language Printing in Frappe

Frappe supports multi-language printing using the `_()` translation function.

All user-visible strings in the print format are wrapped with `{{ _("text") }}`. During rendering, Frappe replaces these strings with their translated versions based on the active language.



# J1 - Jinja Print Format: Job Card Receipt
### How Frappe Determines the Language

1. Frappe first checks the **current user's language preference** in the User settings.
2. If no language is set, it uses the **System Default Language** defined in System Settings.
3. When a print format is rendered, Frappe searches its **translation dictionary** for matching translations.
4. If a translation exists, it replaces the string automatically.
5. If no translation is available, the original English string is displayed.

This mechanism allows the same print format template to support multiple languages without changing the code.





## Data Fetching Patterns in Frappe Print Formats

### 1. Using `frappe.get_all()` inside Jinja Template

In this pattern, database queries are written directly inside the Jinja template.

Example:

{% set jobs = frappe.get_all("Job Card",
    filters={"customer_name": doc.customer_name},
    fields=["name", "device_type"]
) %}

{% for job in jobs %}
{{ job.name }} - {{ job.device_type }}
{% endfor %}

**Explanation:**  
When the print format is rendered, the template executes `frappe.get_all()` and fetches data from the database.

**Drawback:**  
This mixes database logic with the presentation layer and may cause performance issues if many queries are executed.

---

### 2. Pre-computing Data in `before_print()`

In this approach, data is fetched in the Python controller before the print format is rendered.

Example:

Python controller:

def before_print(self, print_settings=None):
    self.related_jobs = frappe.get_all(
        "Job Card",
        filters={"customer_name": self.customer_name},
        fields=["name", "device_type"]
    )

Template usage:
{% for job in doc.related_jobs %}
{{ job.name }} - {{ job.device_type }}
{% endfor %}

**Explanation:**  
The data is fetched in Python and attached to the document (`self`).  
The template accesses it using `doc.related_jobs`.

**Advantage:**  
This keeps business logic in Python and makes the template cleaner and easier to maintain.

### Conclusion
Using `before_print()` to pre-compute data is the recommended approach because it separates business logic from the template.



## Raw Printing vs HTML-PDF Rendering in Frappe

### Raw Printing (ESC/POS)

Raw printing sends printer commands directly to a thermal printer using the ESC/POS protocol.  
Instead of rendering HTML, the system sends low-level commands such as text alignment, line breaks, and barcode instructions.

Characteristics:
- Used mainly for **thermal receipt printers**.
- Very fast because it bypasses browser rendering.
- Limited formatting capabilities.
- Does not support HTML or CSS.

Example commands include:
- Text formatting
- Line feeds
- Barcode printing

---

# J2 - Raw Print vs HTML to PDF
### HTML to PDF Printing (WeasyPrint)

Frappe normally generates print formats using **HTML and CSS**, then converts them to PDF using **WeasyPrint**.

Process:
1. Jinja template generates HTML.
2. CSS styles are applied.
3. WeasyPrint converts the HTML into a PDF document.

Advantages:
- Rich layout support.
- CSS styling.
- Works with normal printers.

Limitations:
- Some browser CSS features are not supported.


### CSS Properties That Work in Browsers but Fail in WeasyPrint

Some modern CSS features supported in browsers may not work correctly in WeasyPrint. Examples include:

- `position: sticky`
- `flexbox gap`
- `backdrop-filter`

Because of this, print formats should use simpler CSS layouts such as tables or basic block elements.



## Using format_value() for Numeric Fields

In Frappe print formats, numeric fields such as Currency should be displayed using the `format_value()` function.

Example without formatting:
{{ doc.final_amount }}

Output:
1000.0

This output does not include the currency symbol and may not follow the correct decimal formatting.

Example using format_value():
{{ frappe.format_value(doc.final_amount, {"fieldtype":"Currency"}) }}

Output:
₹ 1,000.00

Using `format_value()` ensures that numeric values are displayed correctly according to the field type, including the currency symbol, decimal precision, and system locale settings.

Therefore, all numeric fields in the template should use `format_value()` for proper formatting.



# K1 - Background Jobs: Queues, Timeouts, Progress
## Background Job Queues in Frappe

Frappe uses background workers to process tasks asynchronously using `frappe.enqueue()`.  
Jobs are placed into different queues depending on how long they take to execute.

### Default Queue
The **default** queue is used for normal background tasks that are not extremely quick or very heavy.

Examples:
- Updating records
- Processing moderate data tasks
- Sending notifications

### Short Queue
The **short** queue is used for quick tasks that should execute immediately and should not wait behind heavy jobs.

Examples:
- Sending emails
- Small background updates
- Quick notifications

### Long Queue
The **long** queue is used for time-consuming or resource-intensive tasks.

Examples:
- Generating large reports
- Data imports
- Bulk data processing

### Summary
Using different queues ensures that small tasks are not delayed by long-running jobs and helps maintain better system performance.

# K2 - Scheduler Events & Cron
->Disabling Scheduler for a Specific Site

-The scheduler for a specific site can be disabled using the following command:

bench --site <site-name> set-config pause_scheduler 1

-This command updates the site configuration and prevents the scheduler from running background jobs for that site.

To enable the scheduler again:

bench --site <site-name> set-config pause_scheduler 0
Why disable it on a development site?

On a development site, developers may disable the scheduler to prevent automatic background jobs such as emails, reports, or scheduled tasks from running. This helps avoid unnecessary operations and allows developers to manually test and debug scheduled jobs.

What Happens if the Worker is Down?

When a scheduled job is triggered, it is placed in a Redis queue. If the worker process is down at that time, the job remains in the queue and is not executed immediately.

Once the worker starts again, it processes the pending jobs in the queue, and the queued tasks will run normally.

# L1 - REST Resource API & Custom API:

1. List Job Cards
This request retrieves the list of available Job Card documents.

Request
GET /api/resource/Job Card

Description
Returns a list of Job Card records stored in the system.

Sample Response
{
 "data": [
  {
   "name": "JC-0001"
  },
  {
   "name": "JC-0002"
  }
 ]
}

2. Retrieve a Single Job Card

This request fetches the details of a specific Job Card using its document name.

Request
GET /api/resource/Job Card/JC-0001

Description
Returns all fields related to the specified Job Card.

Sample Response
{
 "data": {
  "name": "JC-0001",
  "customer": "Rahul",
  "status": "Open"
 }
}
3. Create a Spare Part

This request creates a new record in the Spare Part DocType.

Request
POST /api/resource/Spare Part

Request Body
{
 "part_name": "Battery",
 "price": 1500
}

Description
Creates a new Spare Part entry with the provided details.

Sample Response
{
 "data": {
  "name": "PART-0001",
  "part_name": "Battery",
  "price": 1500
 }
}

4. Update a Spare Part:
This request updates an existing Spare Part record.

Request
PUT /api/resource/Spare Part/PART-0001

Request Body
{
 "price": 1800
}

Description
Updates the specified field in the Spare Part record.

Sample Response
{
 "data": {
  "name": "PART-0001",
  "price": 1800
 }
}

5. Delete a Spare Part
This request deletes a Spare Part record from the system.

Request
DELETE /api/resource/Spare Part/PART-0001

Description
Removes the specified Spare Part document from the database.

Sample Response
{
 "message": "ok"
}

Summary
The Resource API in Frappe provides a simple way to perform CRUD operations on DocTypes using standard HTTP methods.

Method	Purpose:
GET	--Retrieve records
POST--create new record
PUT	--Update existing record
DELETE	--Remove record

Using these endpoints, developers can easily integrate Frappe with external systems or build custom applications that interact with the Frappe backend.


# Task B - Token Authentication
Difference Between Session Authentication and Token Authentication

Session Cookie Authentication uses a session ID (sid) that is created when a user logs into Frappe through the browser. The browser automatically sends this cookie with each request, so the server can identify the logged-in user.

Token Authentication uses an API key and API secret instead of a login session. These credentials are sent in the request header as:

Authorization: token api_key:api_secret
Appropriate Usage

Session Authentication: is best suited for browser-based applications, because the browser manages the session cookie automatically after login.

Token Authentication : is best suited for server-to-server communication, external integrations, or mobile apps, where maintaining a browser session is not practical.




# Task A - N+1 query detection and fix:
Problem: frappe.get_doc() is called inside the loop causing N+1 queries.

->Fixed Code:

job_cards = frappe.get_all("Job Card", fields=["name", "assigned_technician"])

tech_ids = [jc.assigned_technician for jc in job_cards]

technicians = frappe.get_all(
    "Technician",
    filters={"name": ["in", tech_ids]},
    fields=["name", "technician_name", "phone"]
)

tech_map = {t.name: t for t in technicians}
for jc in job_cards:
    tech = tech_map.get(jc.assigned_technician)
    if tech:
        print(tech.technician_name, tech.phone)



# Task C - Indexing

# K3 - Performance Engineering
Search indexes should not be added to every field because they increase database overhead. Each index must be updated during INSERT, UPDATE, and DELETE operations, which slows down write performance and increases storage usage. Therefore, indexes should only be added to frequently searched or filtered fields to balance performance.


# M1 - Server Script DocType 

Server Script Sandbox Analysis
1. Python functions/modules blocked in Server Script sandbox

Server Scripts run inside a sandbox environment in Frappe.
This environment restricts access to unsafe Python modules.

Examples of blocked modules/functions:

os
subprocess
socket
requests
open() (file operations)

These are blocked to protect the server from malicious code execution.

2. Three things we cannot do in Server Scripts
Things allowed in App Code but not in Server Scripts:

Access the file system (create/read/write files).
Run system commands using os or subprocess.
Use external Python libraries or network requests.
Server Scripts only allow safe and limited operations.

3. When Server Scripts are acceptable:
Server Scripts are suitable for small business logic changes.

Examples:
Automatically set a field value when a document is saved.
Add simple validation (e.g., prevent saving if amount = 0).

4. When App Code should be used instead:
App code should be used for complex or scalable logic.

Examples:
Integrating with external APIs (SMS, payment gateways).
Creating background jobs, reports, or complex business workflows.

5. Governance and Maintainability Risk:
Server Scripts are stored in the database instead of version-controlled code.

This can cause issues such as:
Changes are not tracked in Git.
Harder to review and maintain.
Hidden logic may affect system behavior.

For long-term projects, important logic should be implemented in app code instead of Server Scripts.


## M2 - Task A: What Frappe Caches in Redis

### What is Redis Cache?
Redis is a fast in-memory storage.
Frappe stores frequently needed data in Redis
so it does not hit the database every time.
This makes page loads faster.


### Explored in Bench Console
#### frappe.cache.get_value("bootinfo")
Returns the boot data package sent to browser
when a user first logs in.
If empty returns None - means cache not built yet.

#### frappe.cache.get_keys("")
Shows all keys currently stored in Redis.
Found keys like:
- bootinfo||Administrator
- lang:en
- doctype_meta:Job Card
- user_permissions:Administrator

#### frappe.clear_cache()
Clears everything stored in Redis.
After running - browser reloads slower
because server rebuilds all data
from database again.


### 5 Things Frappe Caches in Redis
#### 1. bootinfo
What it is:
Data package sent to browser when user logs in.

Contains:
- Logged in user name and email
- User roles and permissions
- Enabled modules and apps
- Language and timezone settings
- Custom boot values (quickfix_shop_name,
  quickfix_manager_email)


#### 2. DocType Metadata / Meta
What it is:
Field definitions, form layout, permissions
for every DocType.

Contains:
- All field names and types
- Mandatory fields
- Depends on conditions
- Permission rules


#### 3. Website Context
What it is:
Data for portal and website pages.

Contains:
- Web page content
- Portal menu items
- Website settings
- SEO fields like title and description


#### 4. Translations
What it is:
All translated strings for each language.

Cache key: lang:en (for English)
           lang:ta (for Tamil)

Contains:
- All _("string") translations
- All __("string") JS translations
- Language specific date formats


#### 5. User Permissions
What it is:
Which records each user is allowed to access.

Contains:
- Permission query conditions
- User roles
- Document level permissions
- Default values per user



# M2 - Caching, Redis & Cache Invalidation

## Cache Issues After Changes (Frappe)
1. Browser Shows Old JS After Changing JavaScript
Problem:
After modifying a JavaScript file, the browser still loads the old version of the JS.

Solution:
Run the following command to clear and rebuild assets:

bench build --app quickfix
What this Command Does?

Rebuilds the JavaScript and CSS assets of the app.
Clears the asset cache.

Ensures the browser loads the latest JS changes.
You may also refresh the browser using Ctrl + Shift + R to force reload.

2. Old Field Labels After DocType Changes
Problem

After modifying a DocType (for example changing field labels), users still see the old labels.
Solution

Run:
bench clear-cache

What this Command Does
Clears the DocType metadata cache.
Forces Frappe to reload the latest DocType configuration from the database.


# M3 - Logging, Error Handling & Observability :


Error log:
Error log record Fields-Title,status,Reference Doctype,Refernce Name,ID.


RQ job:
Failed background jobs can be viewed in System --> RQ Job.
If a job fails, its status appears as Failed. In the RQ dashboard, the job can be requeued, which moves it back to the queue so the worker can retry executing it.




# Task C - Production debugging pattern:

Production Debugging Pattern:
When a bug occurs only in production and cannot be reproduced in development, debugging can be done using Error Logs, Audit Logs, and structured logging without enabling developer mode.

Check Error Log:
Navigate to Setup -> Error Log to identify the exception, traceback, method, and timestamp of the failure.

Analyze the Traceback:
The traceback helps determine which function or line of code caused the issue.

Review Audit Logs:
Audit Logs help trace user actions and document changes that may have triggered the bug.

Use frappe.logger for structured logging:
Add logging statements using frappe.logger() to track execution flow and identify where the process fails.

Example:
logger = frappe.logger("quickfix")
logger.info("Webhook started")
logger.warning("Missing configuration")
logger.error("Webhook request failed")

Analyze log files:
Check the log files in sites/site-name/logs/ to understand the sequence of events leading to the error. This approach allows safe debugging in production without enabling developer mode. 




# N1 - Security Audit :

 ## Task A - SQL injection prevention (complete audit):

 ### SQL Injection Prevention – Security Audit
## 1. Finding where user input touches database queries

In this project, user input is received through API methods using function parameters and request data such as frappe.form_dict.

Example:
job_card_name = frappe.form_dict.get("job_card_name")

These inputs are then used in database operations like:
frappe.get_doc()
frappe.db.exists()
frappe.get_list()

Example from the code:
doc = frappe.get_doc("Job Card", job_card)

Here, job_card is user input and it is used to fetch data from the database.
However, these methods are part of Frappe ORM, which internally uses safe queries and prevents SQL injection.

In the codebase, there are also direct SQL queries like:
frappe.db.sql("""
SELECT status, COUNT(name)
FROM `tabJob Card`
GROUP BY status
""")

These queries do not use user input, so they are safe.

## 2. Unsafe vs Safe Query Examples

Even though the project does not currently use unsafe SQL queries, the difference between unsafe and safe queries is shown below.

->Pattern 1 – Single Condition Query
-->Unsafe (f-string)

name = frappe.form_dict.get("name")

frappe.db.sql(f"""
SELECT * FROM `tabJob Card`
WHERE name = '{name}'
""")

This is unsafe because user input is directly inserted into the SQL query.

-->Safe (Parameterized Query)

frappe.db.sql("""
SELECT * FROM `tabJob Card`
WHERE name = %s
""", (name,))

Here %s is used as a placeholder and the value is passed separately.
This prevents SQL injection.

->Pattern 2 – Multiple Conditions
-->Unsafe (f-string)

customer = frappe.form_dict.get("customer")
status = frappe.form_dict.get("status")

frappe.db.sql(f"""
SELECT name
FROM `tabJob Card`
WHERE customer = '{customer}'
AND status = '{status}'
""")

User input is directly placed inside the query.

-->Safe (Parameterized Query)

frappe.db.sql("""
SELECT name
FROM `tabJob Card`
WHERE customer = %s
AND status = %s
""", (customer, status))

Here the database safely inserts the values using placeholders.

## 3. Using frappe.db.escape()

Frappe also provides a function called frappe.db.escape() which can escape user input.

Example:
safe_name = frappe.db.escape(name)

This helps remove dangerous characters from the input.However, frappe.db.escape() is not preferred as much as parameterized queries. This is because escaping still mixes the user input with the SQL query string. If it is not used carefully everywhere, it may still lead to security issues.And the parameterized queries are preferred because they automatically separate SQL code from user data and provide better protection against SQL injection.


# Task B - allow_guest risks:

The /track-job endpoint allows guest users to check job status using a phone number.

### If input validation is not implemented, the following attacks are possible:

Data enumeration attack – An attacker can try many phone numbers to discover job details of different customers.

SQL injection attack – If the phone input is used directly in a SQL query, malicious input could modify the query and expose sensitive data.

API abuse / brute force – Since the endpoint allows guest access, attackers can send many requests to overload the server or collect customer data.

### To reduce these risks:
Phone input is sanitized to allow digits only and a maximum of 10 characters.

The system checks that at least one job exists for the phone number before returning data.

A rate limiter is added to restrict how many times the endpoint can be called.


## Locations where ignore_permissions=True is used:

1. custom_get_count() – Audit logging
doc.insert(ignore_permissions=True)

Justification:
This is used to insert an Audit Log record whenever a count query is executed. The log entry is created by the system to record activity, so bypassing user permission checks is acceptable.


2. mark_ready_for_delivery()
doc.save(ignore_permissions=True)

Justification:
This function updates the job card status as part of an internal workflow. Since it is a system-controlled update rather than a direct user action, bypassing permission checks is acceptable.


3. check_low_stock() – Scheduled job logging
doc.insert(ignore_permissions=True)

Justification:
This function runs as a scheduled background job to check low stock conditions and log the execution. Because it is a system-initiated action and not triggered by a user, bypassing permission checks is acceptable.


### Security Risk Analysis

If a malicious developer or intern adds ignore_permissions=True inside a function that is exposed using:

@frappe.whitelist(allow_guest=True)

it would allow any unauthenticated user to perform database operations without permission checks.

This could allow attackers to create, modify, or delete records without proper authorization, leading to serious data integrity and security issues.

Therefore, ignore_permissions=True should never be used inside guest-accessible endpoints and must only be used in trusted backend system operations such as background jobs or internal logging.



## Task D - Private vs public files:

### When to Use Public Files vs Private Files

Public Files:
Public files are used when the file can be accessed by anyone without login or special permission. These files are suitable for content that is meant to be shared openly, such as website images, public documents, brochures, or other static assets.

Private Files:
Private files are used when the file contains sensitive or restricted information. These files require the user to be logged in and have the proper permissions to access them. Examples include internal company documents, job card attachments, customer data, and confidential reports.



## Issues with Hardcoded API Keys

Hardcoding API keys directly inside Python source code is insecure. If the code is shared or pushed to a repository, the API key becomes visible to anyone who has access to the code. This can allow attackers to misuse the API key to access services or perform unauthorized actions. It also makes it difficult to change the key because the source code must be modified and redeployed.

## Reading Secrets from site_config.json

In Frappe applications, sensitive values such as API keys should be stored in site_config.json and accessed using frappe.conf.get().

### Example:
api_key = frappe.conf.get("payment_api_key")

This allows secrets to be managed outside the source code and keeps them secure.

## Why Secrets Should Not Be in common_site_config.json

common_site_config.json is shared by all sites in a bench instance. If secrets are stored there, every site will use the same key. This increases security risks because if one site is compromised, the secret could be exposed for all sites. Therefore, secrets should be stored in the specific site_config.json for each site.

## Risk of Committing site_config.json to Git

The site_config.json file contains sensitive information such as database passwords and API keys. If this file is committed to a Git repository, these secrets become visible to others and may be exposed publicly. Even if the file is later removed, it remains in the Git history. To prevent this, site_config.json should always be added to .gitignore.



## Debugging Email Failure

If an email fails to send in Frappe, we can check three places:

Email Queue – Go to Email -> Email Queue and check the email status (Sent, Not Sent, or Error). The error message here often shows why the email failed.

SMTP / Email Account Settings – Verify the SMTP server, port, username, password, and TLS/SSL settings in the Email Account. Wrong configuration can prevent emails from sending.

Error Log – Go to Setup -> Error Log to see system errors related to email sending, such as authentication or connection issues.




## Portal Page and SEO Implementation

A public portal page /track-job was created in the www folder to allow customers to track their repair status. Pages inside the www directory are automatically public in Frappe, so the page can be accessed without login. To maintain security, the page only displays non-sensitive information such as Job ID, Customer Name, and Status.

The page uses the get_context() function in track-job.py to fetch Job Card details and pass them to the HTML template for display.

Basic SEO settings were added by setting context.title, context.description, and context.og_title in get_context() so that the page has a proper title and description for browsers and search engines.

The page was also added to the website navigation menu by configuring portal_menu_items in hooks.py, allowing users to easily access the Track Job page from the website menu.