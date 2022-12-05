# Copyright (c) 2022, Srushti Shah And Foram Shah and contributors
# For license information, please see license.txt

import frappe
import json
from frappe.model.document import Document

class WhatsAppBulkTemplateMessages(Document):
	# pass
	@frappe.whitelist()
	def create_receiver_list(self):
		rec = ""
		if self.send_to == "All Lead (Lead)":
			rec = frappe.db.sql(
				"""select whatsapp_no from `tabLead` where ifnull(whatsapp_no,'')!='' and docstatus != 2 and status='Lead'"""
			)
			# print(rec)
		elif self.send_to == "All Lead (Open)":
			rec = frappe.db.sql(
				"""select whatsapp_no from `tabLead` where
				ifnull(whatsapp_no,'')!='' and docstatus != 2 and status='Open'"""
			)
			# print(rec)		
		elif self.send_to == "All Lead (Opportunity)":
			rec = frappe.db.sql(
				"""select whatsapp_no from `tabLead` where
				ifnull(whatsapp_no,'')!='' and docstatus != 2 and status='Opportunity'"""
			)
			# print(rec)
		elif self.send_to == "All Lead (Quotation)":
			rec = frappe.db.sql(
				"""select whatsapp_no from `tabLead` where
				ifnull(whatsapp_no,'')!='' and docstatus != 2 and status='Quotation'"""
			)
		rec_list = ""
		
		# print(type(rec_list))
		for d in rec:
			rec_list += d[0] + "\n"
		print(rec_list)
		self.receiver_list = rec_list
