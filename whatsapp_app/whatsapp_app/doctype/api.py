import datetime
import json

import frappe
import requests
from frappe.model.document import Document
from frappe.utils import now


# @frappe.whitelist()
def bulk_templates(template, l_mobile, doctype=''):
    list = []
    list.clear()
    h = template
    values = {'name': h}
    # this was the basic formula for inner join For the offical usage 
    value2 = frappe.db.sql(
        """SELECT p.name_in_doctype  FROM `tabParameters`p INNER JOIN `tabTemplates`t ON p.parent = %(name)s and t.name = %(name)s;""",
        values=values)
    value2_n = frappe.db.sql(
        """SELECT p.name_in_wati  FROM `tabParameters`p INNER JOIN `tabTemplates`t ON p.parent = %(name)s and t.name = %(name)s;""",
        values=values)
    value_v = []
    if len(value2) > 0:
        for i in value2:
            for i1 in i:
                value_v.append(i1)
                # print(i1)
    else:
        value_v = ["value"]

    value_n = []
    if len(value2_n) > 0:
        for i in value2_n:
            for i1 in i:
                value_n.append(i1)
                # print(i1)
    else:
        value_n = ["name"]

    final_values = []
    for i in value_v:
        # print(i)
        if i == 'value':
            return 'Terminate'
        else:
            final_values.append(frappe.db.get_value(f"{doctype}", filters={'whatsapp_no': l_mobile}, fieldname=[f'{i}']))
    for i in range(0, len(final_values)):
        dict = {"name": value_n[i], "value": final_values[i]}
        list.append(dict)
    return list


def whatsapp_keys_details():
    access_token = frappe.db.get_single_value('WhatsApp Api', 'access_token')
    api_endpoint = frappe.db.get_single_value('WhatsApp Api', 'api_endpoint')
    name_type = frappe.db.get_single_value('WhatsApp Api', 'name_type')
    version = frappe.db.get_single_value('WhatsApp Api', 'version')
    return access_token, api_endpoint, name_type, version


def set_data_in_wati_call_log(number, response):
    f_data = frappe.db.get_value("wati call message log", f"{number}", "data")
    if f_data is not None:
        raw_data = json.loads(f_data)
        response_data = json.loads(response.text)
        raw_data['data'].append(response_data)
        data = json.dumps(raw_data)
        frappe.db.set_value('wati call message log', f'{number}', {'data': f'{data}'})
    else:
        data = {"data": []}
        response_data = json.loads(response.text)
        data['data'].append(response_data)
        data = json.dumps(data)
        doc = frappe.get_doc({"doctype": "wati call message log", "phone": f"{number}", "data": f"{data}"})
        doc.insert()
        frappe.db.commit()

@frappe.whitelist(allow_guest=True)
def send_register_message(name='', number='', type=''):
    # global template
    if frappe.db.get_single_value('WhatsApp Api', 'disabled'):
        return 'Your WhatsApp api key is not set or may be disabled'
    wa_name = ''
    if type == 'supplier':
        template = 'register_template_for_suplier'
        wa_name = 'supplier_name'
    elif type == 'customer':
        template = 'customer_registration_template'
        wa_name = 'name'
    number = int(number)
    access_token, api_endpoint, name_type, version = whatsapp_keys_details()
    headers = {
        "Content-Type": "text/json",
        "Authorization": access_token
    }
    url = f"{api_endpoint}/{name_type}/{version}/sendTemplateMessage?whatsappNumber=91{number}"
    payload = {
        "parameters": [
            {
                "name": wa_name,
                "value":  name
            },
        ],
        "broadcast_name": template,
        "template_name": template
    }
    response = requests.post(url, json=payload, headers=headers)
    set_data_in_wati_call_log(number, response)
    data = json.loads(response.text)
    return data['validWhatsAppNumber']


# whatsapp_app.whatsapp_app.doctype.api.bulk_messages
@frappe.whitelist()
def send_messages(l_mobile=0, template='', l_name='', ):
    if frappe.db.get_single_value('WhatsApp Api', 'disabled'):
        return 'Your WhatsApp api key is not set or may be disabled'
    if l_name:
        l_mobile = frappe.db.get_value("Lead", f"{l_name}", "phone")

    if frappe.db.get_single_value('WhatsApp Api', 'disabled'):
        return 'Your WhatsApp api key is not set or may be disabled'

    access_token, api_endpoint, name_type, version = whatsapp_keys_details()
    headers = {
        "Content-Type": "text/json",
        "Authorization": access_token
    }
    mobile_nos = " ".join(l_mobile.split()).split()
    for mobile in mobile_nos:
        mobile = int(mobile)
        url = f"{api_endpoint}/{name_type}/{version}/sendTemplateMessage?whatsappNumber=91{mobile}"
        if template != '':
            doctype = frappe.db.get_value("Templates", template, ['template_doctype'])
            bt = bulk_templates(template=template, l_mobile=mobile, doctype=doctype)
            if bt == 'Terminate':
                payload = {
                    "broadcast_name": template,
                    "template_name": template
                }
            else:
                payload = {
                    "parameters": bt,
                    "broadcast_name": template,
                    "template_name": template
                }
            response = requests.post(url, json=payload, headers=headers)
        else:
            url = f"{api_endpoint}/{name_type}/{version}/sendSessionMessage/91{mobile}?messageText={message}"
            response = requests.post(url, headers=headers)
    return response


@frappe.whitelist(allow_guest=True)
def send(name='', number='', requesttype='', equipment='', textarea=''):
    if frappe.db.get_single_value('WhatsApp Api', 'disabled'):
        return 'Your WhatsApp api key is not set or may be disabled'
    template = 'new_chat_v1'
    number = int(number)
    access_token, api_endpoint, name_type, version = whatsapp_keys_details()
    headers = {
        "Content-Type": "text/json",
        "Authorization": access_token
    }
    url = f"{api_endpoint}/{name_type}/{version}/sendTemplateMessage?whatsappNumber=91{number}"
    print("\n\n url", url)
    print("api", api_endpoint)
    payload = {
        "parameters": [
            {
                "name": "name",
                "value": name
            },
        ],
        "broadcast_name": template,
        "template_name": template
    }
    print("\n\n before")
    response = requests.post(url, json=payload, headers=headers)
    print("\n\n after")



@frappe.whitelist()
def send_whatsapp_message(number, message='', template_name=''):
    # number = int(number)
    if frappe.db.get_single_value('WhatsApp Api', 'disabled'):
        return 'Your WhatsApp api key is not set or may be disabled'
    access_token, api_endpoint, name_type, version = whatsapp_keys_details()
    headers = {
        "Content-Type": "text/json",
        "Authorization": access_token
    }
    url = f"{api_endpoint}/{name_type}/{version}/sendTemplateMessage?whatsappNumber=91{number}"
    if template_name != '':
        doctype = frappe.db.get_value("Templates", template_name, ['template_doctype'])
        bt = bulk_templates(template=template_name, l_mobile=number, doctype=doctype)
        if bt == 'Terminate':
            payload = {
                "broadcast_name": template_name,
                "template_name": template_name
            }
        else:
            payload = {
                "parameters": bt,
                "broadcast_name": template_name,
                "template_name": template_name
            }
        response = requests.post(url, json=payload, headers=headers)
        set_data_in_wati_call_log(number, response)
        return response.text
    else:
        url = f"{api_endpoint}/{name_type}/{version}/sendSessionMessage/91{number}?messageText={message}"
        response = requests.post(url, headers=headers)
        set_data_in_wati_call_log(number, response)
        return response.text

@frappe.whitelist()
def get_method(mobile, message=""):
    if frappe.db.get_single_value('WhatsApp Api', 'disabled'):
        return 'Your WhatsApp api key is not set or may be disabled'
    number = mobile
    access_token, api_endpoint, name_type, version = whatsapp_keys_details()
    headers = {
        "Content-Type": "text/json",
        "Authorization": access_token
    }
    url = f"{api_endpoint}/{name_type}/{version}/sendSessionMessage/91{number}?messageText={message}"
    response = requests.post(url, headers=headers)
    # print("\n\n message", response.text, "\n\n")


@frappe.whitelist()
def check_status(number):
    old = frappe.db.get_value("wati call message log", filters={"phone": number}, fieldname=["time"])
    if old:
        new = datetime.datetime.strptime(now(), "%Y-%m-%d %H:%M:%S.%f")
        date = new - old
        days, seconds = date.days, date.seconds
        hours = days * 24 + seconds // 3600
        # minutes = (seconds % 3600) // 60
        # seconds = seconds % 60
        if hours <= 23:
            return 'yes'
        else:
            return 'no'
    else:
        return 'no'

@frappe.whitelist()
def get_template_list(doctype):
    return frappe.db.get_list("Templates", filters={"template_doctype": doctype}, pluck = "name")
