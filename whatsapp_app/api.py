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

def message_read(**kwargs):
    wa_data = frappe.local.form_dict
    id = wa_data["id"]
    data = frappe.db.get_list("wati call message log", fields=["data"], limit_start=0, limit_page_length=0)
    for i in data:
        data = json.loads(i['data'])
        for j in data["data"]:
            if "id" in j:
                if j["id"] == id:
                    waid = j["waId"][-10:]
                    frappe.db.set_value("wati call message log", waid, "client_read", 1)
                    frappe.db.commit()
                    break
                    

def comment(**kwargs):
    wa_data = frappe.local.form_dict
    se_mo = wa_data["waId"][-10:]
    message = wa_data["text"]
    l_name = frappe.db.get_value('Lead', filters={"whatsapp_no": se_mo}, fieldname=["name"])
    lead_name = frappe.db.get_value('Lead', filters={"whatsapp_no": se_mo}, fieldname=["lead_name"])
    s_name = frappe.db.get_value('Supplier', filters={"whatsapp_no": se_mo}, fieldname=["name"])
    supplier_name = frappe.db.get_value('Supplier', filters={"whatsapp_no": se_mo}, fieldname=["supplier_name"])
    o_name = frappe.db.get_value('Opportunity', filters={"whatsapp": se_mo}, fieldname=["name"])
    opportunity_name = frappe.db.get_value('Opportunity', filters={"whatsapp": se_mo}, fieldname=["title"])
    r_name = frappe.db.get_value('Raw Data', filters={"whatsapp_no": se_mo}, fieldname=["name"])
    raw_name = frappe.db.get_value('Raw Data', filters={"whatsapp_no": se_mo}, fieldname=["full_name"])
    c_name = frappe.db.get_value('Customer', filters={"whatsapp_no": se_mo}, fieldname=["name"])
    customer_name = frappe.db.get_value('Customer', filters={"whatsapp_no": se_mo}, fieldname=["customer_name"])
    e_name = frappe.db.get_value('Item', filters={"whatsapp_no": se_mo}, fieldname=["name"])
    equipment_name = frappe.db.get_value('Item', filters={"whatsapp_no": se_mo}, fieldname=["name"])


    content = f"<div class='card'><b style='color:orange' class='px-2 pt-2'><i class='fa fa-whatsapp' aria-hidden='true'> Whatsapp Message Received: </i></b> <span class='px-2 pb-2'>{message}</span></div>"

    if l_name:
        set_comment('Lead', l_name, lead_name, content)
        set_notification_log('Lead', l_name, lead_name, message)
    if s_name is not None:
        set_comment('Supplier', s_name, supplier_name, content)
        set_notification_log('Supplier', s_name, supplier_name, message)
    if o_name is not None:
        set_comment('Opportunity', o_name, opportunity_name, content)
        set_notification_log('Opportunity', o_name, opportunity_name, message)
    if r_name is not None:
        set_comment('Raw Data', r_name, raw_name, content)
        set_notification_log('Raw Data', r_name, raw_name, message)
    if c_name is not None:
        set_comment('Customer', c_name, customer_name, content)
        set_notification_log('Opportunity', c_name, customer_name, message)
    if e_name is not None:
        set_comment('Item', e_name, equipment_name, content)
        set_notification_log('Item', e_name, equipment_name, message)

    return 'okey'


def set_comment(doctype, r_name, owner, content):
    activity = frappe.get_doc(
        {"doctype": "Comment", "comment_type": "Info",
         "reference_doctype": doctype, "reference_name": r_name,
         "content": content})
    activity.insert(ignore_permissions=True)
    frappe.db.commit()

    comment = frappe.get_last_doc('Comment')
    frappe.db.set_value('Comment', f'{comment.name}', {"owner": owner})
    frappe.db.commit()


def set_notification_log(doctype, doctype_name, name, content):

    name1 = frappe.db.get_value("Notification Log", filters={"document_type": doctype, "document_name": doctype_name, "type": "Alert", "read": 0}, fieldname=["name"])
    subject = frappe.db.get_value("Notification Log", filters={"document_type": doctype, "document_name": doctype_name, "type": "Alert", "read": 0}, fieldname=["subject"])
    if name1 is not None:
        frappe.db.set_value("Notification Log", name1, "subject", f"{subject}<br>{content}")
    else:
        data = frappe.get_doc({
            "doctype": "Notification Log",
            "subject": f"New <b style='color:green'><i class='fa fa-whatsapp' aria-hidden='true'></i> Whatsapp</b> Message From <b style='color:green'>{name}</b><br>{content}",
            "for_user": "nilesh@sanskartechnolab.com",
            "type": "Alert",
            "document_type": doctype,
            "document_name": doctype_name
        })
        data.insert(ignore_permissions=True)
        frappe.db.commit()


@frappe.whitelist(allow_guest=True)
def wati_webhooks():
    data1 = frappe.call(data, **frappe.form_dict)
    frappe.call(comment, **frappe.form_dict)
    # frappe.call(notification_log, **frappe.form_dict)
    return data1

@frappe.whitelist(allow_guest=True)
def wati_read_webhooks():
    data = frappe.call(message_read, **frappe.form_dict)



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



@frappe.whitelist(allow_guest=True)
def wati_r_webhooks():
    data1 = frappe.call(r_data, **frappe.form_dict)
    return data1


def r_data(**kwargs):
    wa_data = frappe.local.form_dict
    data = {"data": []}

    data['data'].append(wa_data)

    data1 = json.dumps(data)

    doc = frappe.get_doc({"doctype": "wati call message log", "phone": 7990915951, "data": f"{data1}", "read": 0, "time": now()})

    doc.insert()
    frappe.db.commit()
        # frappe.db.set_value("wati call message log", f'{se_mo}', "read", 0)
    return 'success'



@frappe.whitelist(allow_guest=True)
def sent_template_message_webhook():
    response = frappe.form_dict
    if response["templateName"] == "compliance_update":
        data = frappe.db.get_value("Wati Webhook Template Sent", {"whatsapp_no": response["waId"]}, ["name"])
        if data:
            wtsw = frappe.get_doc("Wati Webhook Template Sent", data)
            wtsw.whatsapp_id = response["whatsappMessageId"]
            wtsw.data = frappe.as_json(response, 4)
            wtsw.save(ignore_permissions=True)
            frappe.db.commit()


@frappe.whitelist(allow_guest=True)
def template_message_replied():
    response = frappe.form_dict
    doc = frappe.db.get_value("Wati Webhook Template Sent", filters={"whatsapp_id": f'{response["whatsappMessageId"]}'}, fieldname=["name"])
    if doc:
        if response["text"] == "Yes":
            frappe.db.set_value("Wati Webhook Template Sent", doc, {'is_replied': 1, 'replied_text': "Yes"})
            frappe.db.commit()
        elif response["text"] == "No":
            frappe.db.set_value("Wati Webhook Template Sent", doc, {'is_replied': 1, 'replied_text': "No"})
            frappe.db.commit()
        # if response["text"] == "Yes":
        #     equipment_list = frappe.db.get_list("Whatsapp Equipment", {"parent": doc}, pluck="name")
        

    # doc = frappe.db.get_value(
    #     "Wati Webhook Template Sent",
    #     filters={"whatsapp_id": response["whatsappMessageId"]},
    #     fieldname=["name", "mobile_no", "whatsapp_id", "template_name"],
    #     as_dict=True
    # )

    # # Fetch the child table data from the document
    # child_table_data = frappe.get_all(
    #     "Whatsapp Equipment",
    #     filters={"parent": doc.get("name")},
    #     fields=["equipment_name"],
    #     as_list=False,
    # )

    # # Now, you can access the child table data
    # whatsapp_equipment = child_table_data if child_table_data else []

    # data = frappe.db.get_value("Whatsapp Template Replied", {"whatsapp_no": doc.mobile_no[-10:]}, ["name"])
    # print("\n\n data", data)

    # wtr = frappe.get_doc("Whatsapp Template Replied", data)
    # wtr.replied_text = response["text"]
    # wtr.is_replied = 1
    # wtr.save(ignore_permissions=True)
    # frappe.db.commit()

    # if doc:
    #     # supplier = frappe.db.get_value("Supplier", filters={"whatsapp_no": doc.mobile_no[-10:]}, fieldname=["name", "name_of_suppier"], as_dict=True)
    #     data = frappe.db.get_value("Whatsapp Template Replied", {"whatsapp_no": doc.mobile_no[-10:]}, ["name"])
    #     print("\n\n data", data)
    #     for i in data:
    #         wtr = frappe.get_doc("Whatsapp Template Replied", i)
    #         wtr.replied_text = response["text"]
    #         wtr.is_replied = 1
    #         wtr.save(ignore_permissions=True)
    #         frappe.db.commit()
