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
				"""select mobile_no from `tabLead` where ifnull(mobile_no,'')!='' and docstatus != 2 and status='Lead'"""
			)
			# print(rec)
		elif self.send_to == "All Lead (Open)":
			rec = frappe.db.sql(
				"""select mobile_no from `tabLead` where
				ifnull(mobile_no,'')!='' and docstatus != 2 and status='Open'"""
			)
			# print(rec)		
		elif self.send_to == "All Lead (Opportunity)":
			rec = frappe.db.sql(
				"""select mobile_no from `tabLead` where
				ifnull(mobile_no,'')!='' and docstatus != 2 and status='Opportunity'"""
			)
			# print(rec)
		elif self.send_to == "All Lead (Quotation)":
			rec = frappe.db.sql(
				"""select mobile_no from `tabLead` where
				ifnull(mobile_no,'')!='' and docstatus != 2 and status='Quotation'"""
			)	
			# print(rec)		
		
		# print(type(rec))
		# self.receiver_list = rec


		# list=[]
		print(rec)
		print(type(rec))
		# for i in rec:
		# 	for j in i:
		# 		k = int(j)
		# 		list.append(k)
		# print(list)
		# print(type(list))
		# for i in list:
		# 	self.receiver_list = i

		# self.receiver_list = rec


		# This is to format but its output type is string not tuple 
		rec_list = ""
		
		# print(type(rec_list))
		for d in rec:
			rec_list += d[0] + "\n"
		print(rec_list)
		self.receiver_list = rec_list

		# This is the conversion into list 
		# real_list = json.dumps(rec)
		# self.hidden_list = real_list
		

		# real_list = json.loads(rec)
		# self.hidden_list = real_list
		# print(type(real_list))
		# print(real_list)
