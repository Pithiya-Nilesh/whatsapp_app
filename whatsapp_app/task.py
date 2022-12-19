import json

import requests

import frappe
from whatsapp_app.whatsapp_app.doctype.api import set_data_in_wati_call_log, comment


def whatsapp_keys_details():
    access_token = frappe.db.get_single_value('WhatsApp Api', 'access_token')
    api_endpoint = frappe.db.get_single_value('WhatsApp Api', 'api_endpoint')
    name_type = frappe.db.get_single_value('WhatsApp Api', 'name_type')
    version = frappe.db.get_single_value('WhatsApp Api', 'version')
    return access_token, api_endpoint, name_type, version


def send_report_on_whatsapp():
    return
    # data = frappe.get_doc("wati call message log")
    # data.first_name = "nilesh"
    # data.insert()
    data = frappe.get_doc({"doctype": "wati call message log", "first_name": "nilesh"})
    data.insert()
    frappe.db.commit()
    data = frappe.db.get_list("wati call message log")
    print("\n\n data", data, "\n\n")
    print("\n\n okey its run")


# whatsapp_app.whatsapp_app.doctype.api.bulk_messages
# @frappe.whitelist()
# def send_messages(l_mobile=0, template='welcome_to_new_customer_default_template_v2', l_name='', is_template=True,
#                   message='Hello'):
#     if l_name:
#         l_mobile = frappe.db.get_value("Lead", f"{l_name}", "phone")
#
#     if frappe.db.get_single_value('WhatsApp Api', 'disabled'):
#         return 'Your WhatsApp api key is not set or may be disabled'
#
#     access_token, api_endpoint, name_type, version = whatsapp_keys_details()
#     headers = {
#         "Content-Type": "text/json",
#         "Authorization": access_token
#     }
#     mobile_nos = " ".join(l_mobile.split()).split()
#     print("\n\n mobile no", mobile_nos, "\n\n")
#     for mobile in mobile_nos:
#         mobile = int(mobile)
#         if is_template:
#             url = f"{api_endpoint}/{name_type}/{version}/sendTemplateMessage?whatsappNumber={mobile}"
#             bt = bulk_templates(template, l_mobile=mobile)
#             print("\n\n bt", bt, "\n\n")
#             payload = {
#                 "parameters": bt,
#                 "broadcast_name": template,
#                 "template_name": template
#             }
#             response = requests.post(url, json=payload, headers=headers)
#         else:
#             url = f"{api_endpoint}/{name_type}/{version}/sendSessionMessage/{mobile}?messageText={message}"
#             response = requests.post(url, headers=headers)
#
#         print("\n\n response sdfgaf ", response, "\n\n")
#     return response

    template = 'welcome_to_new_customer_default_template_v2'
    template1 = 'shopify_default_ordershipment_tracking_url_v5'
    # number = int(number)
    number = 7990915950
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
                "value": 'Nilesh'
            },
        ],
        "broadcast_name": template,
        "template_name": template
    }
    print("\n\n before")
    response = requests.post(url, json=payload, headers=headers)
    print("\n\n after")

# ************************************ whatsapp automation schedule ******************************************


def whatsapp_schedule():
    mo_no = 917990915950
    wa_data = [{
        "eventDescription": "Broadcast message with using \"shopify_default_ordershipment_tracking_url_v5\" template was received 24|11|2022",
        "finalText": "Hi, Nilesh Pithiya, your order from adani has been shipped and is on its way.\nTrack your shipment below, thank you.\n\n",
        "template": None,
        "mediaHeaderLink": None,
        "statusString": "FAILED",
        "failedDetail": "Custom params can't have 4 consecutive spaces and button url can't have a space",
        "localMessageId": None,
        "id": "637f2162267008b0938c1c35",
        "created": "2022-11-24T07:46:42.517Z",
        "conversationId": "637de292267008b0938b4422",
        "ticketId": None,
        "eventType": "broadcastMessage",
        "owner": True
    },
    {
        "eventDescription": "Broadcast message with using \"shopify_default_ordershipment_tracking_url_v5\" template was received 24|11|2022",
        "finalText": "Hi, Nilesh Pithiya, your order from adani has been shipped and is on its way.\nTrack your shipment below, thank you.\n\n",
        "template": None,
        "mediaHeaderLink": None,
        "statusString": "FAILED",
        "failedDetail": "Custom params can't have 4 consecutive spaces and button url can't have a space",
        "localMessageId": None,
        "id": "637f1f39267008b0938c1ae3",
        "created": "2022-11-24T07:37:29.163Z",
        "conversationId": "637de292267008b0938b4422",
        "ticketId": None,
        "eventType": "broadcastMessage",
        "owner": False
    },
    {
        "eventDescription": "Broadcast message with using \"shopify_default_ordershipment_tracking_url_v5\" template was received 24|11|2022",
        "finalText": "Hi, Nilesh Pithiya, your order from adani has been shipped and is on its way.\nTrack your shipment below, thank you.\n\n",
        "template": None,
        "mediaHeaderLink": None,
        "statusString": "FAILED",
        "failedDetail": "Custom params can't have 4 consecutive spaces and button url can't have a space",
        "localMessageId": None,
        "id": "637f1f1c267008b0938c1aae",
        "created": "2022-11-24T07:37:00.014Z",
        "conversationId": "637de292267008b0938b4422",
        "ticketId": None,
        "eventType": "broadcastMessage",
        "owner": True
    }]
    data = frappe.db.get_list("Whatsapp Automation Schedule", pluck='name')
    print("\n\n data", data, "\n\n")

    lead_template = frappe.db.get_list("Whatsapp Automation Schedule", filters={'lead_status': 'Lead'}, pluck='name')
    open_template = frappe.db.get_list("Whatsapp Automation Schedule", filters={'lead_status': 'Open'}, pluck='name')
    converted_template = frappe.db.get_list("Whatsapp Automation Schedule", filters={'lead_status': 'Converted'}, pluck='name')
    contact_template = frappe.db.get_list("Whatsapp Automation Schedule", filters={'lead_status': 'Do Not Contact'}, pluck='name')
    replied_template = frappe.db.get_list("Whatsapp Automation Schedule", filters={'lead_status': 'Replied'}, pluck='name')

    lead = (frappe.db.get_list("Lead", filters={'status': 'Lead'}, fields=['phone'], pluck='phone'))
    open = (frappe.db.get_list("Lead", filters={'status': 'Open'}, fields=['phone'], pluck='phone'))
    converted = (frappe.db.get_list("Lead", filters={'status': 'Converted'}, fields=['phone'], pluck='phone'))
    do_not_contact = (frappe.db.get_list("Lead", filters={'status': 'Do Not Contact'}, fields=['phone'], pluck='phone'))
    replied = (frappe.db.get_list("Lead", filters={'status': 'Replied'}, fields=['phone'], pluck='phone'))


#  ************************************************************** #

@frappe.whitelist(allow_guest=True)
def send_register_message():
    # global template
    if frappe.db.get_single_value('WhatsApp Api', 'disabled'):
        return 'Your WhatsApp api key is not set or may be disabled'
    wa_name = ''

    data = frappe.db.get_list("Whatsapp Queue", filters={"status": "Pending"}, fields=["name1", "number", "type"])
    if data:
        names = []
        numbers = []
        types = []

        for i in range(0, len(data)):
            names.append(data[i]["name1"])
        numbers.clear()
        for i in range(0, len(data)):
            numbers.append(data[i]["number"])
        for i in range(0, len(data)):
            types.append(data[i]["type"])

        for i in range(0, len(numbers)):
            number = numbers[i]
            name1 = names[i]
            type1 = types[i]
            name = frappe.db.get_value("Whatsapp Queue", filters={"number": number}, fieldname=['name'])
            frappe.set_value("Whatsapp Queue", name, "status", "In Progress")

            if type1 == 'supplier':
                template = 'register_template_for_suplier'
                wa_name = 'supplier_name'
            elif type1 == 'customer':
                template = 'customer_registration_template'
                wa_name = 'name'
            number = int(number)
            bt = [{"name": wa_name, "value": name1}]
            access_token, api_endpoint, name_type, version = whatsapp_keys_details()
            headers = {
                "Content-Type": "text/json",
                "Authorization": access_token
            }
            url = f"{api_endpoint}/{name_type}/{version}/sendTemplateMessage?whatsappNumber=91{number}"
            payload = {
                "parameters": bt,
                "broadcast_name": template,
                "template_name": template
            }
            response = requests.post(url, json=payload, headers=headers)
            set_data_in_wati_call_log(number, response)
            comment(number, template_name=template, bt=bt)
            data = json.loads(response.text)
            type1 = ''
            name = frappe.db.get_value("Whatsapp Queue", filters={"number": number}, fieldname=['name'])
            if data['validWhatsAppNumber']:
                frappe.set_value("Whatsapp Queue", name, "status", "Sent")
                doctypes = ["Opportunity", "Lead", "Supplier"]
                for doctype in doctypes:
                    if doctype == 'Supplier':
                        name1 = frappe.db.get_value("Supplier", filters={'phone_no': number}, fieldname=["name"])
                        frappe.db.set_value("Supplier", name1, "whatsapp_no", number)
                        frappe.db.commit()
                    if doctype == 'Opportunity':
                        name1 = frappe.db.get_value("Opportunity", filters={'mobile_no': number}, fieldname=["name"])
                        frappe.db.set_value("Opportunity", name1, "whatsapp", number)
                        frappe.db.commit()
                    if doctype == 'Lead':
                        name1 = frappe.db.get_value("Lead", filters={'mobile_no': number}, fieldname=["name"])
                        frappe.db.set_value("Lead", name1, "whatsapp_no", number)
                        frappe.db.commit()
            elif not data['validWhatsAppNumber']:
                frappe.set_value("Whatsapp Queue", name, "status", "Not Valid")

    # return data['validWhatsAppNumber'], number, template, bt


