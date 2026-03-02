import frappe
from quickfix.service_center.doctype.job_card.job_card import JobCard


import frappe
from quickfix.service_center.doctype.job_card.job_card import JobCard


class CustomJobCard(JobCard):

    def validate(self):
        super().validate()

        self._check_urgent_unassigned()


    def _check_urgent_unassigned(self):

        if self.priority == "Urgent" and not self.assigned_technician:

            settings = frappe.get_single("QuickFix Settings")

            frappe.db.commit()   # ✅ ADD HERE

            frappe.enqueue(
                "quickfix.utils.send_urgent_alert",
                job_card=self.name,
                manager=settings.manager_email
            )


    """
    Custom controller overriding Job Card.

    MRO (Method Resolution Order):
    --------------------------------
    MRO defines how Python decides which method to execute
    when multiple classes are involved in inheritance.

    Why super() is NON-NEGOTIABLE:
    --------------------------------
    If we override validate() and do NOT call super().validate(),
    we skip all core validations written in JobCard.

    That can break:
     Mandatory field checks
     Stock validations

    So we have to always call super() first.
    """


"""
Use override_doctype_class when you need to change or
extend the core controller logic (like modifying validate()
internally).

It gives full control over the DocType behavior.

Use doc_events when you only need to add extra logic
without replacing the original controller (safer option).
"""