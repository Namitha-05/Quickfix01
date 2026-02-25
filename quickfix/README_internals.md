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