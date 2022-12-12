# Copyright (c) 2015, Frappe Technologies and Contributors
# License: MIT. See LICENSE
import json

import frappe
from frappe.tests.utils import FrappeTestCase
from frappe.utils import add_to_date, get_link_to_form, today
from frappe.utils.data import is_html

# test_records = frappe.get_test_records('Auto Whatsapp Report')


class TestAutoWhatsappReport(FrappeTestCase):
	def test_auto_whatsapp(self):
		frappe.delete_doc("Auto Whatsapp Report", "Permitted Documents For User")

		auto_whatsapp_report = get_auto_whatsapp_report()

		data = auto_whatsapp_report.get_report_content()

		self.assertTrue(is_html(data))
		self.assertTrue(str(get_link_to_form("Module Def", "Core")) in data)

		auto_whatsapp_report.format = "CSV"

		data = auto_whatsapp_report.get_report_content()
		self.assertTrue('"Language","Core"' in data)

		auto_whatsapp_report.format = "XLSX"

		data = auto_whatsapp_report.get_report_content()

	def test_dynamic_date_filters(self):
		auto_whatsapp_report = get_auto_whatsapp_report()

		auto_whatsapp_report.dynamic_date_period = "Weekly"
		auto_whatsapp_report.from_date_field = "from_date"
		auto_whatsapp_report.to_date_field = "to_date"

		auto_whatsapp_report.prepare_dynamic_filters()

		self.assertEqual(auto_whatsapp_report.filters["from_date"], add_to_date(today(), weeks=-1))
		self.assertEqual(auto_whatsapp_report.filters["to_date"], today())


def get_auto_whatsapp_report():
	if not frappe.db.exists("Auto Whatsapp Report", "Permitted Documents For User"):
		auto_whatsapp_report = frappe.get_doc(
			dict(
				doctype="Auto Whatsapp Report",
				report="Permitted Documents For User",
				report_type="Script Report",
				user="Administrator",
				enabled=1,
				whatsapp_to="test@example.com",
				format="HTML",
				frequency="Daily",
				filters=json.dumps(dict(user="Administrator", doctype="DocType")),
			)
		).insert()
	else:
		auto_whatsapp_report = frappe.get_doc("Auto Whatsapp Report", "Permitted Documents For User")

	return auto_whatsapp_report
