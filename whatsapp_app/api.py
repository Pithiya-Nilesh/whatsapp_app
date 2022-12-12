import datetime
import json


import frappe
from frappe.utils import now


@frappe.whitelist(allow_guest=True)
def get_lead_data(column_name='*', lead_name=None):
    if lead_name:
        return frappe.db.sql(f"select {column_name} from `tabLead` where lead_name='{lead_name}'")
    else:
        return frappe.db.sql(f"select {column_name} from `tabLead`")


@frappe.whitelist(allow_guest=True)
def set_data(first_name, mobile):
    doc = frappe.new_doc('Lead')
    doc.title = first_name
    doc.first_name = first_name
    doc.phone = mobile
    doc.insert()
    return frappe.db.get_value("Lead", {'first_name': first_name}, ['name', 'lead_name', 'first_name', 'last_name', 'phone'], as_dict=1)

def data(**kwargs):
    wa_data = frappe.local.form_dict
    se_mo = wa_data["waId"][-10:]
    f_data = frappe.db.get_value("wati call message log", f"{se_mo}", "data")
    if f_data is not None:
        raw_data = json.loads(f_data)
        raw_data['data'].append(wa_data)
        data = json.dumps(raw_data)
        frappe.db.set_value('wati call message log', f'{se_mo}', {'data': f'{data}', "read": 0, "time": now()})
    else:
        data = {"data": []}
        data['data'].append(wa_data)
        data = json.dumps(data)
        doc = frappe.get_doc({"doctype": "wati call message log", "phone": f"{se_mo}", "data": f"{data}", "read": 0, "time": now()})
        doc.insert()
        frappe.db.commit()
        # frappe.db.set_value("wati call message log", f'{se_mo}', "read", 0)
    return 'success'

@frappe.whitelist(allow_guest=True)
def wati_webhooks():
    data1 = frappe.call(data, **frappe.form_dict)
    return data1


# def send_report_on_whatsapp():
#     data = frappe.get_doc("wati call message log")
#     data.first_name = "nilesh"
#     data.insert()
#     frappe.db.commit()
#     print("\n\n okey its run")

@frappe.whitelist(allow_guest=True)
def comment():
    activity = frappe.get_doc(
        {"doctype": "Comment", "comment_type": "Info", "comment_email": "nilesh@sanskartechnolab.com",
         "reference_doctype": "Lead", "reference_name": "CRM-LEAD-2022-00045",
         "content": "hello this is demo message", "owner": "nilesh@sanskartechnolab.com", "modified_by": "nilesh@sanskartechnoab.com" })
    activity.insert()
    frappe.db.commit()
    return 'okey'


# **************************************************
# def get_linked_call_logs(doctype, docname):
#
#
#     timeline_contents = [{
#         "icon": "call",
#         "is_card": True,
#         "creation": now(),
#         "template": "call_link",
#         "template_data": "asfasf",
#     }]
#
#     return timeline_contents