# Copyright (c) 2022, Srushti Shah And Foram Shah and contributors
# For license information, please see license.txt

import frappe
from frappe import _, msgprint
from frappe.model.document import Document
from frappe.utils import cstr

class Single_whatsapp(Document):
	pass
	# @frappe.whitelist()
	# def create_receiver_list(self):
	# 	# frappe.msgprint("hjdfgjhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhh")
	# 	rec, where_clause = "", ""
	# 	if self.send_to == "All Customer Contact":
	# 		where_clause = " and dl.link_doctype = 'Customer'"
	# 		if self.customer:
	# 			where_clause += (
	# 				" and dl.link_name = '%s'" % self.customer.replace("'", "'")
	# 				or " and ifnull(dl.link_name, '') != ''"
	# 			)
	# 			print("customer")
	# 	if self.send_to == "All Supplier Contact":
	# 		where_clause = " and dl.link_doctype = 'Supplier'"
	# 		if self.supplier:
	# 			where_clause += (
	# 				" and dl.link_name = '%s'" % self.supplier.replace("'", "'")
	# 				or " and ifnull(dl.link_name, '') != ''"
	# 			)
	# 			print("supplier")
	# 	if self.send_to == "All Sales Partner Contact":
	# 		where_clause = " and dl.link_doctype = 'Sales Partner'"
	# 		if self.sales_partner:
	# 			where_clause += (
	# 				"and dl.link_name = '%s'" % self.sales_partner.replace("'", "'")
	# 				or " and ifnull(dl.link_name, '') != ''"
	# 			)
	# 			print("partner")
	# 	if self.send_to in [
	# 		"All Contact",
	# 		"All Customer Contact",
	# 		"All Supplier Contact",
	# 		"All Sales Partner Contact",
	# 	]:
	# 		rec = frappe.db.sql(
	# 			"""select CONCAT(ifnull(c.first_name,''), ' ', ifnull(c.last_name,'')),
	# 			c.mobile_no from `tabContact` c, `tabDynamic Link` dl  where ifnull(c.mobile_no,'')!='' and
	# 			c.docstatus != 2 and dl.parent = c.name%s"""
	# 			% where_clause
	# 		)
	# 		print("contact")

	# 	elif self.send_to == "All Lead (Lead)":
	# 		rec = frappe.db.sql(
	# 			"""select mobile_no from `tabLead` where ifnull(mobile_no,'')!='' and docstatus != 2 and status='Lead'"""
	# 		)
	# 		print(rec)
	# 	elif self.send_to == "All Lead (Open)":
	# 		rec = frappe.db.sql(
	# 			"""select mobile_no from `tabLead` where
	# 			ifnull(mobile_no,'')!='' and docstatus != 2 and status='Open'"""
	# 		)
	# 		print(rec)		
	# 	elif self.send_to == "All Lead (Opportunity)":
	# 		rec = frappe.db.sql(
	# 			"""select mobile_no from `tabLead` where
	# 			ifnull(mobile_no,'')!='' and docstatus != 2 and status='Opportunity'"""
	# 		)
	# 		print(rec)
	# 	elif self.send_to == "All Lead (Quotation)":
	# 		rec = frappe.db.sql(
	# 			"""select mobile_no from `tabLead` where
	# 			ifnull(mobile_no,'')!='' and docstatus != 2 and status='Quotation'"""
	# 		)	
	# 		print(rec)		

	# 	rec_list = ""
	# 	for d in rec:
	# 		# rec_list += d[0] + " - " + d[1] + "\n"
	# 		rec_list += d[0] + "\n"
	# 	self.receiver_list = rec_list
