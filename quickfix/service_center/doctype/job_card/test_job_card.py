# Copyright (c) 2026, Namitha and Contributors
# See license.txt

import frappe
from frappe.tests.utils import FrappeTestCase

class TestJobCard(FrappeTestCase):
    """
    Test class for Job Card DocType
    """

    def test_core_validate_still_runs(self):
        """
        Ensure core validate() runs even after override_doctype_class.

        This test creates a Job Card without a required field (customer)
        and expects Frappe to raise ValidationError.
        """

        # Create invalid Job Card (missing required field 'customer')
        doc = frappe.get_doc({
            "doctype": "Job Card",
            "problem_description": "Test issue"
            # customer intentionally missing
        })

        # Expect ValidationError when inserting invalid document
        self.assertRaises(frappe.ValidationError, doc.insert)