import json

import frappe


def get_context(context):
    context.data = get_data()


@frappe.whitelist()
def get_data():
    mobile = '917990915950'
    chat = frappe.db.get_value("wati call message log", filters={'phone': mobile}, fieldname=["data"])
    data = json.loads(chat)
    return data