# Copyright (c) 2022, Srushti Shah And Foram Shah and contributors
# For license information, please see license.txt
import requests

import frappe
from frappe.model.document import Document


class waticallmessagelog(Document):
	def before_save(self):
		pass
		# print("\n\n data", data, "\n\n")
		# print("\n\n data type", type(data), "\n\n")
