import json

import frappe
import requests
from frappe.model.document import Document


# @frappe.whitelist()
def bulk_templates(template, l_mobile):
    print("\n\n bulk template mobile", l_mobile, "\n\n")
    print("\n\n bulk template template", template, "\n\n")
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
            print("Terminate")
            final_values.append('value')
        else:
            if i == 'lead_name':
                final_values.append(frappe.db.get_value("Lead", filters={'whatsapp_no': l_mobile}, fieldname=['lead_name']))
            if i == 'company':
                final_values.append(frappe.db.get_value("Lead", filters={'whatsapp_no': l_mobile}, fieldname=['company']))
            if i == 'company_name':
                final_values.append(frappe.db.get_value("Lead", filters={'whatsapp_no': l_mobile}, fieldname=['company_name']))
            if i == 'territory':
                final_values.append(frappe.db.get_value("Lead", filters={'whatsapp_no': l_mobile}, fieldname=['territory']))
            if i == 'source':
                final_values.append(frappe.db.get_value("Lead", filters={'whatsapp_no': l_mobile}, fieldname=['source']))
            if i == 'lead_owner':
                final_values.append(frappe.db.get_value("Lead", filters={'whatsapp_no': l_mobile}, fieldname=['lead_owner']))
            if i == 'gender':
                final_values.append(frappe.db.get_value("Lead", filters={'whatsapp_no': l_mobile}, fieldname=['gender']))
    print("This is database values")
    print(final_values)

    for i in range(0, len(final_values)):
        dict = {"name": value_n[i], "value": final_values[i]}
        list.append(dict)
    print(list)
    print(type(list))
    print("this is values of value_v")
    print(value_v)
    print("\n\n list", list, "\n\n")
    return list


def whatsapp_keys_details():
    access_token = frappe.db.get_single_value('WhatsApp Api', 'access_token')
    api_endpoint = frappe.db.get_single_value('WhatsApp Api', 'api_endpoint')
    name_type = frappe.db.get_single_value('WhatsApp Api', 'name_type')
    version = frappe.db.get_single_value('WhatsApp Api', 'version')
    return access_token, api_endpoint, name_type, version


# whatsapp_app.whatsapp_app.doctype.api.bulk_messages
@frappe.whitelist()
def send_messages(l_mobile=0, template='new_chat_v1', l_name='', is_template=True,
                  message='Hello'):
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
    print("\n\n mobile no", mobile_nos, "\n\n")
    for mobile in mobile_nos:
        mobile = int(mobile)
        if is_template:
            url = f"{api_endpoint}/{name_type}/{version}/sendTemplateMessage?whatsappNumber=91{mobile}"
            bt = bulk_templates(template, l_mobile=mobile)
            print("\n\n bt", bt, "\n\n")
            payload = {
                "parameters": bt,
                "broadcast_name": template,
                "template_name": template
            }
            response = requests.post(url, json=payload, headers=headers)
        else:
            url = f"{api_endpoint}/{name_type}/{version}/sendSessionMessage/91{mobile}?messageText={message}"
            response = requests.post(url, headers=headers)

        print("\n\n response sdfgaf ", response, "\n\n")
    return response


@frappe.whitelist(allow_guest=True)
def send(name='', number='', requesttype='', equipment='', textarea=''):
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


@frappe.whitelist(allow_guest=True)
def send_register_message(name='', number='', type=''):
    # global template
    from frappe.utils import now
    # wa_data = {'created': frappe.utils.now(), 'text': message, 'timestamp': frappe.utils.now(), 'eventType': 'message',
    #            'waId': number}
    wa_name = ''
    wa_data = {}
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
    # f_data = frappe.db.get_value("wati call message log", f"{number}", "data")
    # if f_data is not None:
    #     raw_data = json.loads(f_data)
    #     raw_data['data'].append(wa_data)
    #     data = json.dumps(raw_data)
    #     frappe.db.set_value('wati call message log', f'{number}', {'data': f'{data}'})
    # else:
    #     data = {"data": []}
    #     data['data'].append(wa_data)
    #     data = json.dumps(data)
    #     doc = frappe.get_doc({"doctype": "wati call message log", "phone": f"{number}", "data": f"{data}"})
    #     doc.insert()
    #     frappe.db.commit()
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


@frappe.whitelist()
def send_whatsapp_message(number, message=''):
    # number = int(number)
    from frappe.utils import now
    wa_data = {'created': frappe.utils.now(),'text': message,'timestamp':frappe.utils.now(),'eventType':'message','waId':number}
    access_token, api_endpoint, name_type, version = whatsapp_keys_details()
    headers = {
        "Content-Type": "text/json",
        "Authorization": access_token
    }
    url = f"{api_endpoint}/{name_type}/{version}/sendSessionMessage/{number}?messageText={message}"
    f_data = frappe.db.get_value("wati call message log", f"{number}", "data")
    if f_data is not None:
        raw_data = json.loads(f_data)
        raw_data['data'].append(wa_data)
        data = json.dumps(raw_data)
        frappe.db.set_value('wati call message log', f'{number}', {'data': f'{data}'})
    else:
        data = {"data": []}
        data['data'].append(wa_data)
        data = json.dumps(data)
        doc = frappe.get_doc({"doctype": "wati call message log", "phone": f"{number}", "data": f"{data}"})
        doc.insert()
        frappe.db.commit()
    response = requests.post(url, headers=headers)
    return response


@frappe.whitelist()
def get_method(mobile):
    # access_token = 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJqdGkiOiIyMmU0OWVlNy0xMjE4LTQzMDItOGZlNi1kMDQ2NTdhYzNhOWEiLCJ1bmlxdWVfbmFtZSI6Im5pbGVzaEBzYW5za2FydGVjaG5vbGFiLmNvbSIsIm5hbWVpZCI6Im5pbGVzaEBzYW5za2FydGVjaG5vbGFiLmNvbSIsImVtYWlsIjoibmlsZXNoQHNhbnNrYXJ0ZWNobm9sYWIuY29tIiwiYXV0aF90aW1lIjoiMTEvMjMvMjAyMiAwOToxMTozMCIsImRiX25hbWUiOiJ3YXRpX2FwcCIsImh0dHA6Ly9zY2hlbWFzLm1pY3Jvc29mdC5jb20vd3MvMjAwOC8wNi9pZGVudGl0eS9jbGFpbXMvcm9sZSI6IlRSSUFMIiwiZXhwIjoxNjY5ODUyODAwLCJpc3MiOiJDbGFyZV9BSSIsImF1ZCI6IkNsYXJlX0FJIn0.YBO59DKeDAUsmhktWjTuuhDWq6LO1EjOTGs-CQntuJ4'
    # api_endpoint = 'https://app-server.wati.io'
    # name_type = 'api'
    # version = 'v1'
    # # return access_token, api_endpoint, name_type, version
    #
    # # access_token, api_endpoint, name_type, version = whatsapp_keys_details()
    # headers = {"Content-Type": "application/json; charset=utf-8", "Authorization": access_token}
    #
    # # mobile = 917990915950
    # # url = f"{api_endpoint}/{name_type}/{version}/getMessages/917990915950"
    # url = f'https://app-server.wati.io/api/v1/getMessages/{mobile}'
    # print("\n\nurl", url)
    #
    # response = requests.get(url, headers=headers)
    # print("\n\n response.text", response.text, "\n\n")
    # # print("\n\n response", response, "\n\n")
    # return response
    # *******************************************************************************************************************


    # ****************************************************************************
    # wa_data = {"id": "message.Id", "waId": "917990915950", }
    #
    # se_mo = wa_data["waId"]
    # f_data, name = frappe.db.get_value("wati call message log", filters={"phone": f"{se_mo}"},
    #                                    fieldname=["data", "name"])
    #
    # if f_data is not None:
    #     raw_data = json.loads(f_data)
    #     raw_data['data'].append(wa_data)
    #     data = json.dumps(raw_data)
    #     frappe.db.set_value('wati call message log', f'{name}', 'data', f'{data}')
    # else:
    #     data = {"data": []}
    #     data['data'].append(wa_data)
    #     data = json.dumps(data)
    #     frappe.db.set_value('wati call message log', f'{name}', 'data', f'{data}')
    pass


# def send_report_on_whatsapp():
#     data = frappe.get_doc("wati call message log")
#     data.first_name = "nilesh"
#     data.insert()
#     frappe.db.commit()
#     print("\n\n okey its run")

