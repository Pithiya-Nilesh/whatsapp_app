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

def comment(**kwargs):
    wa_data = frappe.local.form_dict
    se_mo = wa_data["waId"][-10:]
    message = wa_data["text"]
    l_name = frappe.db.get_value('Lead', filters={"whatsapp_no": se_mo}, fieldname=["name"])
    lead_name = frappe.db.get_value('Lead', filters={"whatsapp_no": se_mo}, fieldname=["lead_name"])
    s_name = frappe.db.get_value('Supplier', filters={"whatsapp_no": se_mo}, fieldname=["name"])
    supplier_name = frappe.db.get_value('Supplier', filters={"whatsapp_no": se_mo}, fieldname=["supplier_name"])
    o_name = frappe.db.get_value('Opportunity', filters={"whatsapp_no": se_mo}, fieldname=["name"])
    opportunity_name = frappe.db.get_value('Opportunity', filters={"whatsapp_no": se_mo}, fieldname=["title"])

    content = f"<div class='card'><b style='color: green' class='px-2 pt-2'>Whatsapp Message Received: </b> <span class='px-2 pb-2'>{message}</span></div>"

    if l_name:
        set_comment('Lead', l_name, lead_name, content)
    if s_name is not None:
        set_comment('Supplier', s_name, supplier_name, content)
    if o_name:
        set_comment('Opportunity', o_name, opportunity_name, content)

    return 'okey'

def set_comment(doctype, r_name, owner, content):
    activity = frappe.get_doc(
        {"doctype": "Comment", "comment_type": "Info",
         "reference_doctype": doctype, "reference_name": r_name,
         "content": content})
    activity.insert()
    frappe.db.commit()

    comment = frappe.get_last_doc('Comment')
    frappe.db.set_value('Comment', f'{comment.name}', {"owner": owner})
    frappe.db.commit()

@frappe.whitelist(allow_guest=True)
def wati_webhooks():
    data1 = frappe.call(data, **frappe.form_dict)
    frappe.call(comment, **frappe.form_dict)
    return data1


# def send_report_on_whatsapp():
#     data = frappe.get_doc("wati call message log")
#     data.first_name = "nilesh"
#     data.insert()
#     frappe.db.commit()
#     print("\n\n okey its run")


@frappe.whitelist(allow_guest=True)
def message_received():
    return frappe.call(comment, **frappe.form_dict)

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