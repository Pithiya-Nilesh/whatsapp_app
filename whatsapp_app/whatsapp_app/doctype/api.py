import datetime
import json
import sys
from time import sleep
from frappe.utils import now, getdate
import frappe
from frappe.utils.data import today
from frappe.utils.file_manager import save_file_on_filesystem, delete_file, delete_file_from_filesystem
import requests
from frappe.model.document import Document
from frappe.utils import add_to_date
from datetime import datetime
from frappe.utils import now_datetime
from collections import defaultdict
import re
import weasyprint
import os

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
        elif doctype =='Opportunity':
            final_values.append(frappe.db.get_value(f"{doctype}", filters={'whatsapp': l_mobile}, fieldname=[f'{i}']))
        elif doctype == 'Equipment':
            final_values.append(frappe.db.get_value("Item", filters={'whatsapp_no': l_mobile}, fieldname=[f'{i}']))
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
def send_register_message(name='', number='', types='', equipment_name=''):
    global template
    if frappe.db.get_single_value('WhatsApp Api', 'disabled'):
        return 'Your WhatsApp api key is not set or may be disabled'
    wa_name = ''
    wa_name1 = ''
    wa_name2 = ''
    if types == 'supplier':
        template = 'register_template_for_suplier'
        wa_name = 'supplier_name'
    elif types == 'customer':
        template = 'customer_registration_template'
        wa_name = 'name'
    elif types == 'inquiry':
        template = 'equipment_inquiry'
        wa_name1 = 'name'
        wa_name2 = 'equipment_name'


    number = int(number)
    bt = [{"name": wa_name, "value": name}]
    bt1 = [{"name": wa_name1, "value": name}, {"name": wa_name2, "value": equipment_name}]
    access_token, api_endpoint, name_type, version = whatsapp_keys_details()
    headers = {
        "Content-Type": "text/json",
        "Authorization": access_token
    }
    url = f"{api_endpoint}/{name_type}/{version}/sendTemplateMessage?whatsappNumber=91{number}"
    if types == 'inquiry':
        payload = {
            "parameters": bt1,
            "broadcast_name": template,
            "template_name": template
        }
        response = requests.post(url, json=payload, headers=headers)
        set_data_in_wati_call_log(number, response)
        # comment(number, template_name=template, bt=bt)
        data = json.loads(response.text)
        return data['validWhatsAppNumber'], number, template, bt1
    else:
        payload = {
            "parameters": bt,
            "broadcast_name": template,
            "template_name": template
        }
        response = requests.post(url, json=payload, headers=headers)
        set_data_in_wati_call_log(number, response)
        # comment(number, template_name=template, bt=bt)
        data = json.loads(response.text)
        return data['validWhatsAppNumber'], number, template, bt

# whatsapp_app.whatsapp_app.doctype.api.bulk_messages
# @frappe.whitelist()
# def send_messages(l_mobile=0, template='', l_name='', ):
#     if frappe.db.get_single_value('WhatsApp Api', 'disabled'):
#         return 'Your WhatsApp api key is not set or may be disabled'
#     if l_name:
#         l_mobile = frappe.db.get_value("Lead", f"{l_name}", "phone")

#     access_token, api_endpoint, name_type, version = whatsapp_keys_details()
#     headers = {
#         "Content-Type": "text/json",
#         "Authorization": access_token
#     }
#     mobile_nos = " ".join(l_mobile.split()).split()
#     for mobile in mobile_nos:
#         mobile = int(mobile)
#         url = f"{api_endpoint}/{name_type}/{version}/sendTemplateMessage?whatsappNumber=91{mobile}"
#         if template != '':
#             doctype = frappe.db.get_value("Templates", template, ['template_doctype'])
#             bt = bulk_templates(template=template, l_mobile=mobile, doctype=doctype)
#             if bt == 'Terminate':
#                 payload = {
#                     "broadcast_name": template,
#                     "template_name": template
#                 }
#             else:
#                 payload = {
#                     "parameters": bt,
#                     "broadcast_name": template,
#                     "template_name": template
#                 }
#             response = requests.post(url, json=payload, headers=headers)
#         else:
#             url = f"{api_endpoint}/{name_type}/{version}/sendSessionMessage/91{mobile}?messageText={message}"
#             response = requests.post(url, headers=headers)
#     return response

@frappe.whitelist()
def send_whatsapp_message(number, message='', template_name='', data='', doctype='', current_date=''):
  
    if frappe.db.get_single_value('WhatsApp Api', 'disabled'):
        return 'Your WhatsApp api key is not set or may be disabled'
    access_token, api_endpoint, name_type, version = whatsapp_keys_details()
    headers = {
        "Content-Type": "text/json",
        "Authorization": access_token
    }
    # template_name1 = frappe.db.get_value("Templates", template_name, "template_name")
    template_name1 = template_name
    url = f"{api_endpoint}/{name_type}/{version}/sendTemplateMessage?whatsappNumber=91{number}"
    if template_name1 != '':
        # doctype = frappe.db.get_value("Templates", template_name, ['template_doctype'])
        # bt = bulk_templates(template=template_name, l_mobile=number, doctype=doctype)

        bt = map_dynamic_filelds_for_wati(number, doctype, data)
        if bt == 'Terminate':
            payload = {
                "broadcast_name": template_name1,
                "template_name": template_name1
            }
        else:
            payload = {
                "parameters": bt,
                "broadcast_name": template_name1,
                "template_name": template_name1
            }
        response = requests.post(url, json=payload, headers=headers)
        set_data_in_wati_call_log(number, response)
        comment(number, template_name=template_name1, bt=bt)
        # return response.text
  
    else:
        url = f"{api_endpoint}/{name_type}/{version}/sendSessionMessage/91{number}?messageText={message}"
        response = requests.post(url, headers=headers)
        set_data_in_wati_call_log(number, response)
        comment(number, message)
        # print("\n\n asdfasdf", response, "\n\n")
        # return response.text
        
    temp_id = frappe.db.get_value("wati call message log", filters={'name': number}, fieldname="data")
    json_data = json.loads(temp_id)
    if json_data['data']:
        json_data['data'][-1]['send_time'] = current_date
    else:
        json_data['data'] = [{
            "send_time": current_date
        }]
    
    frappe.db.set_value("wati call message log", number, 'data', json.dumps(json_data))
    frappe.db.commit()

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
    response = requests.post(url, json=payload, headers=headers)


@frappe.whitelist()
def send_whatsapp_message(number, message='', template_name='', data='', doctype=''):
    # number = int(number)
    if frappe.db.get_single_value('WhatsApp Api', 'disabled'):
        return 'Your WhatsApp api key is not set or may be disabled'
    access_token, api_endpoint, name_type, version = whatsapp_keys_details()
    headers = {
        "Content-Type": "text/json",
        "Authorization": access_token
    }
    # template_name1 = frappe.db.get_value("Templates", template_name, "template_name")
    template_name1 = template_name
    url = f"{api_endpoint}/{name_type}/{version}/sendTemplateMessage?whatsappNumber=91{number}"
    if template_name1 != '':
        # doctype = frappe.db.get_value("Templates", template_name, ['template_doctype'])
        # bt = bulk_templates(template=template_name, l_mobile=number, doctype=doctype)
        bt = map_dynamic_filelds_for_wati(number, doctype, data)
        if bt == 'Terminate':
            payload = {
                "broadcast_name": template_name1,
                "template_name": template_name1
            }
        else:
            payload = {
                "parameters": bt,
                "broadcast_name": template_name1,
                "template_name": template_name1
            }
        response = requests.post(url, json=payload, headers=headers)
        set_data_in_wati_call_log(number, response)
        comment(number, template_name=template_name1, bt=bt)
        return response.text
    else:
        url = f"{api_endpoint}/{name_type}/{version}/sendSessionMessage/91{number}?messageText={message}"
        response = requests.post(url, headers=headers)
        set_data_in_wati_call_log(number, response)
        comment(number, message)
        # print("\n\n asdfasdf", response, "\n\n")
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
    # from frappe.permissions import get_roles

    # Get the roles of the user
    user_roles = frappe.get_roles(frappe.session.user)

    print("user role", user_roles)
    final_template_list = []


    t_list = frappe.db.get_list("Templates", filters={"template_doctype": ['in', [doctype, '']], "status": "APPROVED"}, pluck = "name")
    for i in t_list:
        doc = frappe.get_doc("Templates", i)
        if doc.wati_templates_role:
            for j in doc.wati_templates_role:
                    if j.role in user_roles:
                        final_template_list.append(doc.name)
        else:
            final_template_list.append(doc.name)

    return list(set(final_template_list))

        

    # return frappe.db.get_list("Templates", filters={"template_doctype": ['in', [doctype, '']], "status": "APPROVED"}, pluck = "name")


@frappe.whitelist(allow_guest=True)
def comment(number, message='', template_name='', bt='', bt1=''):
    if bt1:
        bt = json.loads(bt1)
    name = frappe.session.user
    l_name = frappe.db.get_value('Lead', filters={"whatsapp_no": number}, fieldname=["name"])
    o_name = frappe.db.get_value('Opportunity', filters={"whatsapp": number}, fieldname=["name"])
    r_name = frappe.db.get_value('Raw Data', filters={"whatsapp_no": number}, fieldname=["full_name"])
    c_name = frappe.db.get_value('Customer', filters={"whatsapp_no": number}, fieldname=["customer_name"])
    e_name = frappe.db.get_value('Item', filters={"whatsapp_no": number}, fieldname=["name"])
    s_name = frappe.db.get_value('Supplier', filters={"whatsapp_no": number}, fieldname=["name"])
    
    if message != '':
        content = f"<div class='card'><b style='color: green' class='px-2 pt-2'>Whatsapp Message Sent: </b> <span class='px-2 pb-2'>{message}</span></div>"
    else:
        sample = frappe.db.get_value("Templates", filters={'template_name': template_name}, fieldname=["sample"])
        sample = sample.replace("{{", "{")
        sample = sample.replace("}}", "}")
        list1 = []
        keysList = []
        keysList.clear()
        for i in range(0, len(bt)):
            keysList.append(bt[i]["name"])
        list1.clear()
        for i in range(0, len(bt)):
            list1.append(bt[i]["value"])
        res = dict(map(lambda i, j: (i, j), keysList, list1))
        formatted = sample.format(**res)
        content = f"<div class='card'><b style='color: green' class='px-2 pt-2'><i class='fa fa-whatsapp' aria-hidden='true'> Whatsapp Template Sent: </i></b> <a href='/app/templates/{template_name}' class='px-2 pb-2'>{formatted}</a></div>"

    if l_name:
        set_comment('Lead', l_name, name, content)
    if e_name:
        set_comment('Item', e_name, name, content)
    if s_name:
        set_comment('Supplier', s_name, name, content)
    if o_name:
        set_comment('Opportunity', o_name, name, content)
    if r_name:
        set_comment('Raw Data', r_name, name, content)
    if c_name:
        set_comment('Customer', c_name, name, content)
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
def contact_us_message(mobile, doctype):
    name = frappe.db.get_value(doctype, filters={'mobile_no': mobile}, fieldname=["name"])
    if doctype == 'Supplier':
        name = frappe.db.get_value(doctype, filters={'phone_no': mobile}, fieldname=["name"])
    frappe.db.set_value(doctype, name, "whatsapp_no", mobile)
    frappe.db.commit()
    return "okey"


@frappe.whitelist(allow_guest=True)
def send_bulk_whatsapp_message(template_name, doctype, name, data):
    if frappe.db.get_single_value('WhatsApp Api', 'disabled'):
        return 'Your WhatsApp api key is not set or may be disabled'
    name = json.loads(name)
    # template_name1 = frappe.db.get_value("Templates", template_name, "template_name")
    template_name1 = template_name
    number = []
    if doctype == 'Opportunity':
        for i in name:
            number.append(frappe.db.get_value(doctype, i, ["whatsapp"]))
    else:
        for i in name:
            number.append(frappe.db.get_value(doctype, i, ["whatsapp_no"]))
    number = list(filter(lambda item: item is not None, number))
    access_token, api_endpoint, name_type, version = whatsapp_keys_details()
    headers = {
        "Content-Type": "text/json",
        "Authorization": access_token
    }
    # mobile_nos = " ".join(number.split()).split()
    for mobile in number:
        mobile = int(mobile)
        url = f"{api_endpoint}/{name_type}/{version}/sendTemplateMessage?whatsappNumber=91{mobile}"
        if template_name1 != '':
            # bt = bulk_templates(template=template_name, l_mobile=mobile, doctype=doctype)
            # print("\n\n bt", bt, "\n\n")
            bt = map_dynamic_filelds_for_wati(mobile, doctype, data)
            if bt == 'Terminate':
                payload = {
                    "broadcast_name": template_name1,
                    "template_name": template_name1
                }
                print("\n\n WITHOUT PARAMETER:", payload, "\n\n")
            else:
                payload = {
                    "parameters": bt,
                    "broadcast_name": template_name1,
                    "template_name": template_name1
                }
                print("\n\n WITH:", payload, "\n\n")
            response = requests.post(url, json=payload, headers=headers)
            print("\n\n response", response, "\n\n")
            set_data_in_wati_call_log(mobile, response)
            comment(mobile, template_name=template_name1, bt=bt)
        else:
            url = f"{api_endpoint}/{name_type}/{version}/sendSessionMessage/91{mobile}?messageText={message}"
            response = requests.post(url, headers=headers)
    # return response

@frappe.whitelist(allow_guest=True)
def queue_whatsapp(name, number, types):
    whatsapp_queue = frappe.get_doc(
        {"doctype": "Whatsapp Queue", "name1": name,
         "number": number, "type": types, "status": "Pending"})
    whatsapp_queue.insert()
    frappe.db.commit()


@frappe.whitelist(allow_guest=True)
def get_unread_message_number():
    return frappe.db.get_all("wati call message log", filters={'read': 0}, fields=["name"], pluck="name")


@frappe.whitelist(allow_guest=True)
def send_insurance_expiry_reminder_notification():
    if frappe.db.get_single_value('WhatsApp Api', 'disabled'):
        return 'Your WhatsApp api key is not set or may be disabled'
    else:
        date = add_to_date(datetime.now(), days=15, as_string=True)
        data1 = frappe.db.get_list("Item", fields=["supplier_name", "whatsapp_no", "register_no", "equipment_model_no"], filters={"insurance_date": date})
        if data1 and data1['whatsapp_no']:
            template = 'insuranse_expiry_reminder'
            for i in data1:
                supplier_name = i['supplier_name']
                mobile = i['supplier_number']
                equipment_name = i['register_no'] if not None else i['equipment_model_no']
                access_token, api_endpoint, name_type, version = whatsapp_keys_details()
                headers = {
                    "Content-Type": "text/json",
                    "Authorization": access_token
                }
                url = f"{api_endpoint}/{name_type}/{version}/sendTemplateMessage?whatsappNumber=91{mobile}"
                payload = {
                    "parameters": [
                        {
                            "name": "supp_name",
                            "value": supplier_name
                        },
                        {
                            "name": "equipment_name",
                            "value": equipment_name
                        }
                    ],
                    "broadcast_name": template,
                    "template_name": template
                }
                response = requests.post(url, json=payload, headers=headers)

@frappe.whitelist(allow_guest=True)
def send_fitness_expiry_reminder_notification():
    if frappe.db.get_single_value('WhatsApp Api', 'disabled'):
        return 'Your WhatsApp api key is not set or may be disabled'
    else:
        date = add_to_date(datetime.now(), days=15, as_string=True)
        data1 = frappe.db.get_list("Item", fields=["supplier_name", "whatsapp_no", "register_no",
                                                   "equipment_model_no"], filters={"fitness_dt": date})
        if data1 and data1['whatsapp_no']:
            template = 'fitness_certificate_notification'
            for i in data1:
                supplier_name = i['supplier_name']
                mobile = i['supplier_number']
                equipment_name = i['register_no'] if not None else i['equipment_model_no']
                access_token, api_endpoint, name_type, version = whatsapp_keys_details()
                headers = {
                    "Content-Type": "text/json",
                    "Authorization": access_token
                }
                url = f"{api_endpoint}/{name_type}/{version}/sendTemplateMessage?whatsappNumber=91{mobile}"
                payload = {
                    "parameters": [
                        {
                            "name": "s_name",
                            "value": supplier_name
                        },
                        {
                            "name": "e_name",
                            "value": equipment_name
                        }
                    ],
                    "broadcast_name": template,
                    "template_name": template
                }
                response = requests.post(url, json=payload, headers=headers)

        #     mobile_nos = []
        #     supplier_name = []
        #     data = []
        #     mobile_nos.clear()
        #     supplier_name.clear()
        #     data.clear()
        #
        #     for i in data1:
        #         mobile_nos.append(frappe.db.get_value("Supplier", fieldname=["whatsapp_no"], filters={"name": i}))
        #     mobile_nos = [x for x in mobile_nos if x != "" and x is not None]
        #     mobile_nos = [*set(mobile_nos)]
        #     for i in mobile_nos:
        #         supplier_name.append(frappe.db.get_value("Supplier", filters={"whatsapp_no": i}))
        #     for i in supplier_name:
        #         data.append(frappe.db.get_list("Item", filters={"supplier": i, "insurance_dateexpiry_date": date}, fields=["supplier_name", "insurance_dateexpiry_date", "name"]))
        #
        #     print("\n\n data", data, "\n\n")
        #     print("\n\n mobile nos", mobile_nos, "\n\n")
        # return data1
        # ******************************
        # data = frappe.form_dict
        # final = data['data']

@frappe.whitelist(allow_guest=True)
def send_daily_mail_report():
    new_supplier = frappe.db.sql(
        "select count(name)as Supplier from `tabSupplier` where creation between curdate() - interval 2 day and curdate()", as_list=True)
    new_equipment = frappe.db.sql(
        "select count(name)as Equipment from `tabItem` where creation between curdate() - interval 2 day and curdate()", as_list=True)
    total_supplier = frappe.db.get_list("Supplier")
    total_equipment = frappe.db.get_list("Item")
    today = frappe.utils.get_datetime(getdate()).strftime("%d-%b-%Y")

    recipients = [
        'mailto:arjun.pachani@gmail.com',
        'mailto:dhaval.nadpara@migoo.in',
        'mailto:parthdbhimani@gmail.com'
    ]

    message = f'''

        <p>Dear Team Management,</p>
        <p>The updates as of {today} are</p>
        <p>New Supplier Added: {new_supplier[0][0]}</p>
        <p>New Equipment Added: {new_equipment[0][0]}</p>
        <p>Total Supplier: {len(total_supplier)}</p>
        <p>Total Equipment: {len(total_equipment)}</p>

    '''

    frappe.sendmail(
        recipients=recipients,
        subject='Daily Report',
        message=message
    )
    
@frappe.whitelist(allow_guest=True)
def send_expo_form_template(name, number, equipment):
    if frappe.db.get_single_value('WhatsApp Api', 'disabled'):
        return 'Your WhatsApp api key is not set or may be disabled'
    template = 'hire_expo_form'
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
                "name": "c_name",
                "value": name
            },
            {
                "name": "equipment_name",
                "value": equipment
            }
        ],
        "broadcast_name": template,
        "template_name": template
    }
    response = requests.post(url, json=payload, headers=headers)

@frappe.whitelist(allow_guest=True)
def get_template():
    access_token, api_endpoint, name_type, version = whatsapp_keys_details()    
    url = f"{api_endpoint}/{name_type}/{version}/getMessageTemplates"
    headers = {
        "Content-Type": "application/json",
        "Authorization": access_token
    }
    response = requests.post(url, headers=headers)
    data = response.json()
    
    if "messageTemplates" in data:
        templates = data["messageTemplates"]
        all_templates_available = True  

        for template in templates:
            # if template["status"] == "APPROVED":
            if not template["status"] == "DRAFT":
                element_name = template["elementName"]
                status = template["status"]
                body = template["bodyOriginal"]
                header = template["header"]
                img = None
                if header is not None:
                    img = header.get("mediaFromPC")
                existing_template = frappe.get_all(
                    "Templates",
                    filters={"template_name": element_name, "status": status, "sample": body},
                    fields=["name"]
                )
                if not existing_template:
                    all_templates_available = False  
                    new_template = frappe.new_doc("Templates")
                    new_template.template_name = element_name
                    new_template.status = status
                    new_template.sample = body
                    new_template.image = img
                    new_template.insert(ignore_permissions=True)
                    frappe.db.commit()
        
        if all_templates_available:
            frappe.msgprint("All templates are available.")
        else:
            None

# @frappe.whitelist(allow_guest = True)
# def get_template_sample(selected_template, selected_doctype, whatsapp_no):
#     list = bulk_templates(template=selected_template, doctype=selected_doctype, l_mobile=whatsapp_no)
#     content = get_content(selected_template, list)
#     return content

# def get_content(template_name='', bt=''):
#     if template_name == '':
#         return None
#     else:
#         sample = frappe.db.get_value("Templates", filters={'template_name': template_name}, fieldname=["sample"])
#         sample = sample.replace("{{", "{")
#         sample = sample.replace("}}", "}")
#         list1 = []
#         keysList = []
#         keysList.clear()
#         for i in range(0, len(bt)):
#             keysList.append(bt[i]["name"])
#         list1.clear()
#         for i in range(0, len(bt)):
#             list1.append(bt[i]["value"])
#         res = dict(map(lambda i, j: (i, j), keysList, list1))
#         formatted = sample.format(**res)
#         content = f"{formatted}"
#         return content
 
@frappe.whitelist(allow_guest=True)  
def get_template_sample(phone):
    temp_id = frappe.db.get_value("wati call message log", filters={'name': phone}, fieldname="data")
    json_data = json.loads(temp_id)

    for item in json_data['data']:
        if 'template_name' not in item:
            continue
        
        template_name = item['template_name']
        paraJson = item['parameteres']
        values = [param['value'] for param in paraJson]
        
        templates = frappe.db.get_all("Templates", filters={'template_name': template_name}, fields=["template_name", "sample"])

        tempPara = [] 
        template_parameters = {}  
        sample = ""  
        
        for template in templates:
            if 'sample' in template:
                sample = template.get("sample")
                
                tempPara = re.findall(r"{{(.*?)}}", sample)
                
                template_parameters = {
                    "template_name": template.get("template_name"),
                    "parameters": tempPara
                }
        
        replaced_parameters = [values[i] if i < len(values) else param for i, param in enumerate(tempPara)]
        modified_tempPara = {
            "template_name": template_parameters.get("template_name"),
            "parameters": replaced_parameters
        }
        
        modified_sample = sample
        for i, param in enumerate(tempPara):
            modified_sample = modified_sample.replace("{{" + param + "}}", replaced_parameters[i])
        
        item['modified_sample'] = modified_sample 

    frappe.db.set_value("wati call message log", phone, 'data', json.dumps(json_data))
    frappe.db.commit()
    return "OK"
   
@frappe.whitelist(allow_guest=True)
def demo():
    # print("\n\n frappe", demo1, "\n\n")
    template = 'register_template_for_suplier'
    mobile = '7990915950'
    doctype = 'Equipment'
    demo1 = [{"name": "supplier_name",  "is_dynamic": 1, "value": "supplier_name"}, {"name":  "company_name",  "is_dynamic": 1, "value": "whatsapp_no"}, {"name":  "age",  "is_dynamic": 0, "value":  23}]
  
    list = map_dynamic_filelds_for_wati(mobile, 'Equipment', data=demo1)
    
    print("\n\n list", list, "\n\n")


def map_dynamic_filelds_for_wati(l_mobile, doctype='', data=''):
    data1 = json.loads(data)
    list = []
    list.clear()
    value_v = []
    value_n = []
    static = []
    dynamic = []
    for i in data1:
        if i["is_dynamic"] == 1:
            dynamic.append(i)
        if i["is_dynamic"] == 0:
            static.append(i)

    for i in dynamic:
        value_v.append(i["value"])
        value_n.append(i["name"])
   
    final_values = []
    for i in value_v:
        if i == 'value':
            return 'Terminate'
        elif doctype =='Opportunity':
            final_values.append(frappe.db.get_value(f"{doctype}", filters={'whatsapp': l_mobile}, fieldname=[f'{i}']))
        elif doctype == 'Equipment':
            final_values.append(frappe.db.get_value("Item", filters={'whatsapp_no': l_mobile}, fieldname=[f'{i}']))
        else:
            final_values.append(frappe.db.get_value(f"{doctype}", filters={'whatsapp_no': l_mobile}, fieldname=[f'{i}']))
    for i in range(0, len(final_values)):
        dict = {"name": value_n[i], "value": final_values[i]}
        list.append(dict)
    for i in static:
        list.append({"name": i['name'], "value": i["value"]})
    return list


@frappe.whitelist(allow_guest=True)
def get_image(filename):
    access_token, api_endpoint, name_type, version = whatsapp_keys_details()    
    url = f"{api_endpoint}/{name_type}/{version}/getMedia?fileName=data/images/{filename}"
    headers = {
        "Authorization": access_token
    }
    response = requests.request(
    "GET", url, headers=headers)
    if response.content:
        save_file_on_filesystem(fname=filename, content=response.content)


@frappe.whitelist(allow_guest=True)
def get_img(phone):
    temp_id = frappe.db.get_value("wati call message log", filters={'name': phone}, fieldname="data")
    json_data = json.loads(temp_id)

    for item in json_data['data']:
        if 'template_name' not in item:
            continue
        
        template_name = item['template_name']
        
        templateImg = frappe.db.get_all("Templates", filters={'template_name': template_name}, fields=["image"])
        # print(templateImg)
        
        image_filename = ''
        if templateImg:
            image_filename = templateImg[0].get('image', '')
            # print(image_filename)
        
        item['templateImg'] = image_filename 
   
    frappe.db.set_value("wati call message log", phone, 'data', json.dumps(json_data))
    frappe.db.commit()
    return "OK"

# @frappe.whitelist(allow_guest=True)
# def generate_pdf():
#     if frappe.db.get_single_value('WhatsApp Api', 'disabled'):
#             return 'Your WhatsApp api key is not set or may be disabled'
    
#     name = frappe.db.sql("""

#     with insurance as (
#         select 
#             name,
#             supplier,
#             supplier_email,
#             supplier_name,
#             equipment_main_category,
#             register_no,
#             CASE
#                 WHEN rto_register = 'Registered' THEN model
#                 ELSE equipment_model_no
#             END AS "model",
#             insurance_date as 'insurance_dt',
#             DATEDIFF(insurance_date, CURDATE()) as 'insuranceDaysToGo',
#             CONCAT('Insurance') AS 'insurances'
#         from tabItem
#         where
#             insurance_date >= CURDATE()
#             AND DATEDIFF(insurance_date, CURDATE()) <= 15
#     ),
#     fitness as (
#         select 
#             name,
#             supplier,
#             supplier_email,
#             supplier_name,
#             equipment_main_category,
#             register_no,
#             CASE
#                 WHEN rto_register = 'Registered' THEN model
#                 ELSE equipment_model_no
#             END AS "model",
#             fitness_dt as 'fitness_dt',
#             DATEDIFF(fitness_dt, CURDATE()) as 'FitnessDaysToGo',
#             CONCAT('Fitness') AS 'fitnesses'
#         from tabItem
#         where
#             fitness_dt >= CURDATE() 
#             AND DATEDIFF(fitness_dt, CURDATE()) <= 15
#     ),
#     PUC as (
#         select 
#             name,
#             supplier,
#             supplier_email,
#             supplier_name,
#             equipment_main_category,
#             register_no,
#             CASE
#                 WHEN rto_register = 'Registered' THEN model
#                 ELSE equipment_model_no
#             END AS "model",
#             pollution as 'pollution_dt',
#             DATEDIFF(pollution, CURDATE()) as 'PollutionDaysToGo',
#             CONCAT('Pollution') AS 'Pollutions'
#         from tabItem
#         where
#             pollution >= CURDATE()
#             AND DATEDIFF(pollution, CURDATE()) <= 15
#     ),
#     npermit as (
#         select
#             name,
#             supplier,
#             supplier_email,
#             supplier_name,
#             equipment_main_category,
#             register_no,
#             CASE
#                 WHEN rto_register = 'Registered' THEN model
#                 ELSE equipment_model_no
#             END AS "model",
#             npermit_upto as 'npermit_upto_dt',
#             DATEDIFF(npermit_upto, CURDATE()) as 'National_PermitDaysToGo',
#             CONCAT('National Permit') AS 'National_Permits'
#         from tabItem
#         where
#             npermit_upto >= CURDATE()
#             AND DATEDIFF(npermit_upto, CURDATE()) <= 15
#     ),
#     permit_validity as (
#         select
#             name,
#             supplier,
#             supplier_email,
#             supplier_name,
#             equipment_main_category,
#             register_no,
#             CASE
#                 WHEN rto_register = 'Registered' THEN model
#                 ELSE equipment_model_no
#             END AS "model",
#             permit_validity_upto as 'permit_validity_upto_dt',
#             DATEDIFF(permit_validity_upto, CURDATE()) as 'State_PermitDaysToGo',
#             CONCAT('State Permit') AS 'State_Permits'
#         from tabItem
#         where
#             permit_validity_upto >= CURDATE()
#             AND DATEDIFF(permit_validity_upto, CURDATE()) <= 15
#     )
#     select 
#         name,
#         supplier,
#         supplier_email,
#         supplier_name,
#         equipment_main_category,
#         register_no,
#         model,
#         DATE_FORMAT(insurance_dt, '%d-%m-%Y'), 
#         insurances,
#         insuranceDaysToGo
#     from insurance
#     union
#     select 
#         name,
#         supplier,
#         supplier_email,
#         supplier_name,
#         equipment_main_category,
#         register_no,
#         model,
#         DATE_FORMAT(fitness_dt, '%d-%m-%Y'), 
#         fitnesses,
#         FitnessDaysToGo
#     from fitness
#     union
#     select 
#         name,
#         supplier,
#         supplier_email,
#         supplier_name,
#         equipment_main_category,
#         register_no,
#         model,
#         DATE_FORMAT(pollution_dt, '%d-%m-%Y'),
#         Pollutions,
#         PollutionDaysToGo
#     from PUC
#     union
#     select
#         name,
#         supplier,
#         supplier_email,
#         supplier_name,
#         equipment_main_category,
#         register_no,
#         model,
#         DATE_FORMAT(npermit_upto_dt, '%d-%m-%Y'),
#         National_Permits,
#         National_PermitDaysToGo
#     from npermit
#     union
#     select
#         name,
#         supplier,
#         supplier_email,
#         supplier_name,
#         equipment_main_category,
#         register_no,
#         model,
#         DATE_FORMAT(permit_validity_upto_dt, '%d-%m-%Y'),
#         State_Permits,
#         State_PermitDaysToGo
#     from permit_validity
        
#     """)

#    # create a dictionary to store equipment information for each supplier
#     supplier_dict = defaultdict(list)
#     reminder_supllier = []

#     for i in name:
#         equipment_name = i[0]
#         supplier = i[1]
#         supplier_email = i[2]
#         supplier_name =  i[3]
#         equipment_main_category = i[4]
#         register_no = i[5]
#         model = i[6]
#         date = i[7]
#         status = i[8]
#         daystogo = i[9]

#         # add equipment information to supplier dictionary
#         supplier_dict[supplier].append({
#             'equipment_name': equipment_name,
#             'supplier_email': supplier_email,
#             'supplier_name': supplier_name,
#             'equipment_main_category': equipment_main_category,
#             'register_no': register_no,
#             'model': model,
#             'date': date,
#             'status': status,
#             'daystogo': daystogo
#         })
#         if daystogo <= 3:
#             reminder_supllier.append(supplier)


#     # loop through supplier dictionary and send a single email to each supplier
#     for supplier, equipment_list in supplier_dict.items():
#         message = '''
#             <div>
#                 <div class="sec-2">
#                     <h3 style="">Hello, {}</h4>
#                     <p>We are writing to remind you that your Equipment's documents are set to expire. The details are mentioned below.</p>
#                     <table border="1px" cellspacing="0" cellpadding="4" style="border-collapse: collapse;">
#                         <tr style="background-color: #e6992a;">
#                             <th style="border: 1px solid black; padding: 4px;">Compliance</th>
#                             <th style="border: 1px solid black; padding: 4px;">Valid Till</th>
#                             <th style="border: 1px solid black; padding: 4px;">Expiring in</th>
#                             <th style="border: 1px solid black; padding: 4px;">Equipment</th>
#                             <th style="border: 1px solid black; padding: 4px;">Equipment No</th>
#                             <th style="border: 1px solid black; padding: 4px;">Model No</th>
#                         </tr>
#             '''.format(supplier_dict[supplier][0]['supplier_name'])

#         # add equipment information for the current supplier to the email message
#         for equipment in equipment_list:
#             message += '''
#                         <tr>
#                             <td style="border: 1px solid black; padding: 4px; text-align: center;">{}</td>
#                             <td style="border: 1px solid black; padding: 4px; text-align: center;">{}</td>
#                             <td style="border: 1px solid black; padding: 4px; text-align: center;">{} Days to Go</td>
#                             <td style="border: 1px solid black; padding: 4px; text-align: center;">{}</td>
#                             <td style="border: 1px solid black; padding: 4px; text-align: center;">{}</td>
#                             <td style="border: 1px solid black; padding: 4px; text-align: center;">{}</td>
#                         </tr>
#             '''.format(equipment['status'], equipment['date'], equipment['daystogo'], equipment['equipment_main_category'], equipment['register_no'],
#                        equipment['model'])

#         message += '''
#                     </table>
#                 </div>
#             </div>
#             <p>Get it renewed as soon as possible to avoid further inconvenience.</p>
#             <p>Thank you for choosing Migoo. We value your trust and are committed to providing you with the best service possible.</p>
#             <div><b>Thanks & Regards,</b></div>
#             <br>
#             <div><b>Surya Prakash Pal</b></div>
#             <div><b>Assistant Manager</b></div> 
#             <br>
#             <div>
#                 <table>
#                     <tr>
#                         <td style="border-right: 2.5px solid #e6992a; ">
#                             <img
#                                 src="https://ci3.googleusercontent.com/mail-sig/AIorK4zf_Mw4U0lrUBfnOuVQzvYfOGDhx1WSRbMtBaWBErGIoq8nQyLPAziA9SF9qRoUVfH4b4fWMfM">
#                         </td>
#                         <td style="padding-left:12px; color: black;">
#                             <div style="display: flex; margin-bottom: 2px;">
#                                 <img src="https://www.migoo.in/files/call (1).png" height="16px" width="16px"
#                                     style="margin-top: auto; margin-bottom: auto;">
#                                 <div style="margin-left: 5px;">
#                                     +91 79692 12202
#                                 </div>
#                             </div>

#                             <div style="display: flex; margin-bottom: 2px;">
#                                 <img src="https://www.migoo.in/files/email1ead26.png" height="16px" width="16px"
#                                     style="margin-top: auto; margin-bottom: auto;">
#                                 <a style="color: black;" href="mailto:surya@migoo.in" style="text-decoration: none;">
#                                     <div style="margin-left: 5px;">surya@migoo.in</div>
#                                 </a>
#                             </div>

#                             <div style="display: flex; margin-bottom: 2px;">
#                                 <img src="https://www.migoo.in/files/link.png" height="16px" width="16px"
#                                     style="margin-top: auto; margin-bottom: auto;">
#                                 <a style="color: black;" href="https://www.migoo.in">
#                                     <div style="margin-left: 5px;">www.migoo.in</div>
#                                 </a>
#                             </div>

#                             <div style="display: flex; margin-bottom: 2px;">
#                                 <img src="https://www.migoo.in/files/location.png" height="16px" width="16px"
#                                     style="margin-top: auto; margin-bottom: auto;">
#                                 <div style="margin-left: 5px;">Migved Solutions Private Limited,</div>
#                             </div>
#                             <div style="margin-left: 20px;">
#                                 A-1204, Mondeal Heights,
#                                 <br> Iskcon Cross Road, S.G.Highway, <br>
#                                 Ahmedabad-380058
#                             </div>

#                             <div style="margin-top: 10px;">
#                                 <a href="https://www.facebook.com/people/Migoo-Equipments/100087829991875/?mibextid=ZbWKwL"
#                                     target="_blank">
#                                     <img src="https://www.migoo.in/files/facebook.png" style="height: 20px;"></a>

#                                 <a href="https://www.instagram.com/migoo_equipment/?igshid=YmMyMTA2M2Y%3D">
#                                     <img src="https://www.migoo.in/files/instagram.png" style="height: 20px;"></a>

#                                 <a
#                                     href="https://www.linkedin.com/authwall?trk=bf&trkInfo=AQE3GrOu_soLXAAAAYTnfV7Ak5NhrLNM9IxIvNuvfFL51XjUZjWDRN_WROWhhGDHQfI05HuUk46hX4INHsRvXff6X08bFwXCpC3OG-A7nocY7Rtqb7kN1teuUQMukrXRVO5ai84=&original_referer=&sessionRedirect=https%3A%2F%2Fwww.linkedin.com%2Fin%2Fmigoo-equipments-270563257">
#                                     <img src="https://www.migoo.in/files/linkedin.png" style="height: 20px;"></a>

#                                 <a href="https://twitter.com/MigooEquipments">
#                                     <img src="https://www.migoo.in/files/twitter-sign.png" style="height: 20px;"></a>
#                             </div>
#                         </td>
#                     </tr>
#                 </table>
#             </div>

#             <br>
#             <div>

#                 <div style="display: flex; margin-bottom: 2px;">
#                     <img
#                         src="https://lh4.googleusercontent.com/Tg-ugYQdUjAPJTtdSu3Rc8pYT0hONyb7dbg-Z0LN2iYvKbhazcdWIu_Vyn7-m7IIPdU0fd9VwxdDKm90nE6tVaAeQ4_b13OV79O7w9sPJiJP4YOqt2juD4XWgjK4v4E5TmIVuOsY3dDyuQ7p3-B4ndw">
#                     <div style="color: green; margin-left: 5px;">Consider The Environment. Think Before You Print.</div>
#                 </div>
#             </div>
#             '''                           
#         #     print("\n", supplier_dict, "\n")
#         # return supplier_dict
#         s_name = frappe.db.get_value("Supplier", filters={'name': supplier}, fieldname=["name_of_suppier", "whatsapp_no"])  
#         # print("\n", s_name, "\n")
#         if s_name is None:
#             continue
#         name_of_supplier = s_name[0]
#         whatsapp_no = s_name[1]

#         file_path = name_of_supplier.replace(" ", "_").lower() + '.pdf'
#         pdf = weasyprint.HTML(string=message).write_pdf()
        
#         with open(file_path, 'wb') as f:
#             f.write(pdf)
            
#         save_file_on_filesystem(file_path, content=pdf)

#         # create a new document
#         from frappe.utils import today

#         doc = frappe.get_doc({
#             'doctype': 'Sent File',
#             'file_path': file_path,
#             'sent_date': today()
#         })
#         doc.insert(ignore_permissions=True)
#         frappe.db.commit()

#         template = 'compalince_update_remainders_in_cc'
#         number = whatsapp_no
#         access_token, api_endpoint, name_type, version = whatsapp_keys_details()
#         headers = {
#         "Content-Type": "text/json",
#         "Authorization": access_token
#         }

#         from frappe.utils import get_url
#         site_url = get_url()
       
#         file_link = site_url + '/files/' + file_path
        
#         url = f"{api_endpoint}/{name_type}/{version}/sendTemplateMessage?whatsappNumber=91{number}"
#         payload = {
#             "parameters": [
#                 {
#                     "name": "supp_name",
#                     "value": name_of_supplier
#                 },
#                 {
#                     "name": "pdf_link",
#                     "value": file_link
#                 }
#             ],
#             "broadcast_name": template,
#             "template_name": template
#         }
#         if check_daily_message_limit_for_user(number, template):
#             response = requests.post(url, json=payload, headers=headers)

#             data = json.loads(response.text)

#             if "result" in data and data["result"]:
#                 log = frappe.new_doc("Whatsapp Message Daily Limit Log")
#                 log.whatsapp_no = number
#                 log.template_name = template
#                 log.insert()
#                 frappe.db.commit()
#         else:
#             olwtm = frappe.new_doc("Over Limit Whatsapp Template Messages")
#             olwtm.doc_type = "Supplier"
#             olwtm.doc_name = supplier
#             olwtm.template_name = template
#             olwtm.file_url = file_link
#             olwtm.whatsapp_no = number
#             olwtm.insert(ignore_permissions=True)
#             frappe.db.commit()

#     # send reminder if compliance expired in 3 days.
#     supplier_unique_list = list(set(reminder_supllier))

#     for r_supplier in supplier_unique_list:
#         whatsapp_no = frappe.db.get_value("Supplier", filters={'name': r_supplier}, fieldname=["whatsapp_no"])  
#         if whatsapp_no is None:
#             continue
#         # print("asdfasdf \n\n", whatsapp_no)
#         url = f"{api_endpoint}/{name_type}/{version}/sendTemplateMessage?whatsappNumber=91{whatsapp_no}"
#         payload = {
#             "broadcast_name": "compliance_update",
#             "template_name": "compliance_update",
#             "parameters": []
#         }
#         if check_daily_message_limit_for_user(whatsapp_no, "compliance_update"):

#             response = requests.post(url, json=payload, headers=headers)
#             data = json.loads(response.text)

#             if "result" in data and data["result"]:
#                 log = frappe.new_doc("Whatsapp Message Daily Limit Log")
#                 log.whatsapp_no = whatsapp_no
#                 log.template_name = "compliance_update"
#                 log.insert()
#                 frappe.db.commit()

#                 wtsw = frappe.new_doc("Wati Webhook Template Sent")
#                 wtsw.whatsapp_no = '91'+whatsapp_no if whatsapp_no else ''
#                 wtsw.template_name = 'compliance_update'
#                 wtsw.doc_type = "Supplier"
#                 wtsw.doc_name = r_supplier
#                 wtsw.date = add_to_date(datetime.now(), days=3, as_string=True, as_datetime=True)

#                 for equipment in equipment_list:
#                     child_row = wtsw.append("whatsapp_equipment", {})
#                     child_row.equipment_name = equipment["equipment_name"]               

#                 wtsw.insert(ignore_permissions=True)
#                 frappe.db.commit()
#         else:
#             olwtm = frappe.new_doc("Over Limit Whatsapp Template Messages")
#             olwtm.doc_type = "Supplier"
#             olwtm.doc_name = supplier
#             olwtm.template_name = "compliance_update"
#             olwtm.file_url = file_link
#             olwtm.whatsapp_no = whatsapp_no
#             olwtm.insert(ignore_permissions=True)
#             frappe.db.commit()
        

# @frappe.whitelist(allow_guest=True)
# def create_table():
#     # scheduler event
#     enable_cron = frappe.db.get_single_value('Custom Settings', 'enable_cron_job')
#     if enable_cron == 1:
#         from frappe.utils import get_url
#         site_url = get_url()
#         if site_url == "https://www.migoo.in/" or site_url == "https://migoo.in/":
#             return generate_pdf()
#             # return "PDF created"


# @frappe.whitelist(allow_guest=True)
# def send_remider_if_not_repliyed():
#     # scheduler event
#     enable_cron = frappe.db.get_single_value('Custom Settings', 'enable_cron_job')
#     if enable_cron == 1:
#         from frappe.utils import get_url
#         site_url = get_url()
#         if site_url == "https://www.migoo.in/" or site_url == "https://migoo.in/":
#             if frappe.db.get_single_value('WhatsApp Api', 'disabled'):
#                     return 'Your WhatsApp api key is not set or may be disabled'

#             # data = frappe.db.get_list("Wati Webhook Template Sent", filters=[["date", "=", frappe.utils.add_days(frappe.utils.now_datetime(), -6)], ["replied_text", "in", ["No", "whatsapp_no"]]], fields=["name", "whatsapp_no", "doc_type", "doc_name", "template_name"])
#             data = frappe.db.get_list("Wati Webhook Template Sent", filters=[["date", "=", frappe.utils.add_days(frappe.utils.now_datetime(), -3)], ["replied_text", "in", ["No", "whatsapp_no"]]], fields=["name", "whatsapp_no", "doc_type", "doc_name", "template_name"])
            
#             for i in data:
#                 if check_daily_message_limit_for_user(i.whatsapp_no, "compliance_update"):
#                     equipments = frappe.db.get_list("Whatsapp Equipment", {"parent": i.name}, ["equipment_name"])
                    
#                     access_token, api_endpoint, name_type, version = whatsapp_keys_details()
#                     headers = {
#                     "Content-Type": "text/json",
#                     "Authorization": access_token
#                     }

#                     url = f"{api_endpoint}/{name_type}/{version}/sendTemplateMessage?whatsappNumber={i.whatsapp_no}"
#                     payload = {
#                         "broadcast_name": "compliance_update",
#                         "template_name": "compliance_update",
#                         "parameters": []
#                     }
                    
#                     response = requests.post(url, json=payload, headers=headers)
#                     data = json.loads(response.text)

#                     if "result" in data and data["result"]:
#                         log = frappe.new_doc("Whatsapp Message Daily Limit Log")
#                         log.whatsapp_no = i.whatsapp_no
#                         log.template_name = "compliance_update"
#                         log.insert()
#                         frappe.db.commit()

#                         wtsw = frappe.new_doc("Wati Webhook Template Sent")
#                         wtsw.whatsapp_no = i.whatsapp_no if i.whatsapp_no else ''
#                         wtsw.template_name = 'compliance_update'
#                         wtsw.doc_type = i.doc_type
#                         wtsw.doc_name = i.doc_name
#                         wtsw.date = today()

#                         for equipment in equipments:
#                             child_row = wtsw.append("whatsapp_equipment", {})
#                             child_row.equipment_name = equipment["equipment_name"]          

#                         wtsw.insert(ignore_permissions=True)
#                         frappe.db.commit()
#                 else:
#                     olwtm = frappe.new_doc("Over Limit Whatsapp Template Messages")
#                     olwtm.doc_type = i.doc_type
#                     olwtm.doc_name = i.doc_name
#                     olwtm.template_name = "compliance_update"
#                     olwtm.whatsapp_no = i.whatsapp_no
#                     olwtm.insert(ignore_permissions=True)
#                     frappe.db.commit()


@frappe.whitelist(allow_guest=True)
def delete_sent_file():

    from datetime import datetime # from python std library
    from frappe.utils import add_to_date

    before_7_days = add_to_date(datetime.now(), days=-7, as_string=True)
    doc_name = frappe.db.get_list("Sent File", filters=[["sent_date", "<", before_7_days]], fields=["name", "file_path"])
    for name in doc_name:
        delete_file(f"/files/{name.file_path}")
        frappe.delete_doc('Sent File', name.name)
        frappe.db.commit()


@frappe.whitelist(allow_guest=True)
def a():
    ''' this is testing function '''
    # access_token, api_endpoint, name_type, version = whatsapp_keys_details()
    # url = f"{api_endpoint}/{name_type}/{version}/sendTemplateMessage?whatsappNumber=917990915950"
    # headers = {
    #     "Content-Type": "text/json",
    #     "Authorization": access_token
    #     }
    # payload = {
    #     "broadcast_name": "compliance_update",
    #     "template_name": "compliance_update"
    # }
    # response = requests.post(url, json=payload, headers=headers)
    # print("response", response)
    # print("response.text", response.text)

    # return frappe.db.get_list("Whatsapp Message Daily Limit Log", fields=["*"])


    numbers = ["7990915950", "8690396913", "7678767898"]

    for number in numbers:
        if check_daily_message_limit_for_user(number, "aadf"):
            print("\n\n send message")
            log = frappe.new_doc("Whatsapp Message Daily Limit Log")
            log.whatsapp_no = number
            log.template_name = "aadf"
            log.insert()
            frappe.db.commit()
            # continue
        else:
            print("\n\n reach limit")
            # continue


def check_daily_message_limit_for_user(number, template_name):  
    # check dailly limit per user for send template, count past 24 hours message log and if message log reach limit send false else true

    dmlpu = frappe.db.get_single_value('WhatsApp Api', 'daily_message_limit_per_user')
    vt = frappe.db.get_single_value('WhatsApp Api', 'validate_template')
    from frappe.utils import now_datetime, add_to_date

    # Calculate the datetime 24 hours ago from the current time
    twenty_four_hours_ago = add_to_date(now_datetime(), hours=-24)

    if vt == 1:
        whatsapp_log = frappe.db.count('Whatsapp Message Daily Limit Log', {"creation": [">", twenty_four_hours_ago], "whatsapp_no": number, "template_name": template_name})
    else:
        whatsapp_log = frappe.db.count('Whatsapp Message Daily Limit Log', {"creation": [">", twenty_four_hours_ago], "whatsapp_no": number})

    if whatsapp_log >= int(dmlpu):
        # you can`t send message
        return False
    else:
        # you can send message
        return True

def get_compliance_template_count(whatsapp_no, template_name):
    today1 = frappe.utils.nowdate()
    seven_days_ago = frappe.utils.add_days(today1, -7)
    return frappe.db.count("Whatsapp Message Compliance Log", {"whatsapp_no": whatsapp_no, "template_name": template_name, "creation": [">", seven_days_ago]})
        
########################## New UI Code Start ###########################

# @frappe.whitelist(allow_guest=True)
# def generate_pdf_and_store_data():
#     enable_cron = frappe.db.get_single_value('Custom Settings', 'enable_cron_job')
#     if enable_cron == 1:
#         if frappe.db.get_single_value('WhatsApp Api', 'disabled'):
#                 return 'Your WhatsApp api key is not set or may be disabled'
        
#         # send first template
#         lowmtbs = frappe.new_doc("List of WhatsApp Messages to be Sent")

#         name = frappe.db.sql("""

#         with insurance as (
#             select 
#                 name,
#                 supplier,
#                 supplier_email,
#                 supplier_name,
#                 equipment_main_category,
#                 register_no,
#                 CASE
#                     WHEN rto_register = 'Registered' THEN model
#                     ELSE equipment_model_no
#                 END AS "model",
#                 insurance_date as 'insurance_dt',
#                 DATEDIFF(insurance_date, CURDATE()) as 'insuranceDaysToGo',
#                 CONCAT('Insurance') AS 'insurances'
#             from tabItem
#             where
#                 insurance_date >= CURDATE()
#                 AND DATEDIFF(insurance_date, CURDATE()) <= 15
#         ),
#         fitness as (
#             select 
#                 name,
#                 supplier,
#                 supplier_email,
#                 supplier_name,
#                 equipment_main_category,
#                 register_no,
#                 CASE
#                     WHEN rto_register = 'Registered' THEN model
#                     ELSE equipment_model_no
#                 END AS "model",
#                 fitness_dt as 'fitness_dt',
#                 DATEDIFF(fitness_dt, CURDATE()) as 'FitnessDaysToGo',
#                 CONCAT('Fitness') AS 'fitnesses'
#             from tabItem
#             where
#                 fitness_dt >= CURDATE() 
#                 AND DATEDIFF(fitness_dt, CURDATE()) <= 15
#         ),
#         PUC as (
#             select 
#                 name,
#                 supplier,
#                 supplier_email,
#                 supplier_name,
#                 equipment_main_category,
#                 register_no,
#                 CASE
#                     WHEN rto_register = 'Registered' THEN model
#                     ELSE equipment_model_no
#                 END AS "model",
#                 pollution as 'pollution_dt',
#                 DATEDIFF(pollution, CURDATE()) as 'PollutionDaysToGo',
#                 CONCAT('Pollution') AS 'Pollutions'
#             from tabItem
#             where
#                 pollution >= CURDATE()
#                 AND DATEDIFF(pollution, CURDATE()) <= 15
#         ),
#         npermit as (
#             select
#                 name,
#                 supplier,
#                 supplier_email,
#                 supplier_name,
#                 equipment_main_category,
#                 register_no,
#                 CASE
#                     WHEN rto_register = 'Registered' THEN model
#                     ELSE equipment_model_no
#                 END AS "model",
#                 npermit_upto as 'npermit_upto_dt',
#                 DATEDIFF(npermit_upto, CURDATE()) as 'National_PermitDaysToGo',
#                 CONCAT('National Permit') AS 'National_Permits'
#             from tabItem
#             where
#                 npermit_upto >= CURDATE()
#                 AND DATEDIFF(npermit_upto, CURDATE()) <= 15
#         ),
#         permit_validity as (
#             select
#                 name,
#                 supplier,
#                 supplier_email,
#                 supplier_name,
#                 equipment_main_category,
#                 register_no,
#                 CASE
#                     WHEN rto_register = 'Registered' THEN model
#                     ELSE equipment_model_no
#                 END AS "model",
#                 permit_validity_upto as 'permit_validity_upto_dt',
#                 DATEDIFF(permit_validity_upto, CURDATE()) as 'State_PermitDaysToGo',
#                 CONCAT('State Permit') AS 'State_Permits'
#             from tabItem
#             where
#                 permit_validity_upto >= CURDATE()
#                 AND DATEDIFF(permit_validity_upto, CURDATE()) <= 15
#         )
#         select 
#             name,
#             supplier,
#             supplier_email,
#             supplier_name,
#             equipment_main_category,
#             register_no,
#             model,
#             DATE_FORMAT(insurance_dt, '%d-%m-%Y'), 
#             insurances,
#             insuranceDaysToGo
#         from insurance
#         union
#         select 
#             name,
#             supplier,
#             supplier_email,
#             supplier_name,
#             equipment_main_category,
#             register_no,
#             model,
#             DATE_FORMAT(fitness_dt, '%d-%m-%Y'), 
#             fitnesses,
#             FitnessDaysToGo
#         from fitness
#         union
#         select 
#             name,
#             supplier,
#             supplier_email,
#             supplier_name,
#             equipment_main_category,
#             register_no,
#             model,
#             DATE_FORMAT(pollution_dt, '%d-%m-%Y'),
#             Pollutions,
#             PollutionDaysToGo
#         from PUC
#         union
#         select
#             name,
#             supplier,
#             supplier_email,
#             supplier_name,
#             equipment_main_category,
#             register_no,
#             model,
#             DATE_FORMAT(npermit_upto_dt, '%d-%m-%Y'),
#             National_Permits,
#             National_PermitDaysToGo
#         from npermit
#         union
#         select
#             name,
#             supplier,
#             supplier_email,
#             supplier_name,
#             equipment_main_category,
#             register_no,
#             model,
#             DATE_FORMAT(permit_validity_upto_dt, '%d-%m-%Y'),
#             State_Permits,
#             State_PermitDaysToGo
#         from permit_validity
            
#         """)

#     # create a dictionary to store equipment information for each supplier
#         supplier_dict = defaultdict(list)
#         reminder_supllier = []

#         for i in name:
#             equipment_name = i[0]
#             supplier = i[1]
#             supplier_email = i[2]
#             supplier_name =  i[3]
#             equipment_main_category = i[4]
#             register_no = i[5]
#             model = i[6]
#             date = i[7]
#             status = i[8]
#             daystogo = i[9]

#             # add equipment information to supplier dictionary
#             supplier_dict[supplier].append({
#                 'equipment_name': equipment_name,
#                 'supplier_email': supplier_email,
#                 'supplier_name': supplier_name,
#                 'equipment_main_category': equipment_main_category,
#                 'register_no': register_no,
#                 'model': model,
#                 'date': date,
#                 'status': status,
#                 'daystogo': daystogo
#             })
#             if daystogo <= 7:
#                 reminder_supllier.append(supplier)


#         # loop through supplier dictionary and send a single email to each supplier
#         for supplier, equipment_list in supplier_dict.items():

#             message = '''
#                 <div>
#                     <div class="sec-2">
#                         <h3 style="">Hello, {}</h4>
#                         <p>We are writing to remind you that your Equipment's documents are set to expire. The details are mentioned below.</p>
#                         <table border="1px" cellspacing="0" cellpadding="4" style="border-collapse: collapse;">
#                             <tr style="background-color: #e6992a;">
#                                 <th style="border: 1px solid black; padding: 4px;">Compliance</th>
#                                 <th style="border: 1px solid black; padding: 4px;">Valid Till</th>
#                                 <th style="border: 1px solid black; padding: 4px;">Expiring in</th>
#                                 <th style="border: 1px solid black; padding: 4px;">Equipment</th>
#                                 <th style="border: 1px solid black; padding: 4px;">Equipment No</th>
#                                 <th style="border: 1px solid black; padding: 4px;">Model No</th>
#                             </tr>
#                 '''.format(supplier_dict[supplier][0]['supplier_name'])

#             with_reminder = 0
#             # add equipment information for the current supplier to the email message
#             for equipment in equipment_list:
#                 message += '''
#                             <tr>
#                                 <td style="border: 1px solid black; padding: 4px; text-align: center;">{}</td>
#                                 <td style="border: 1px solid black; padding: 4px; text-align: center;">{}</td>
#                                 <td style="border: 1px solid black; padding: 4px; text-align: center;">{} Days to Go</td>
#                                 <td style="border: 1px solid black; padding: 4px; text-align: center;">{}</td>
#                                 <td style="border: 1px solid black; padding: 4px; text-align: center;">{}</td>
#                                 <td style="border: 1px solid black; padding: 4px; text-align: center;">{}</td>
#                             </tr>
#                 '''.format(equipment['status'], equipment['date'], equipment['daystogo'], equipment['equipment_main_category'], equipment['register_no'],
#                         equipment['model'])

#                 if equipment["daystogo"] <= 7:
#                     with_reminder = 1

#             message += '''
#                        </table>
#                 </div>
#             </div>
#                     <p>Get it renewed as soon as possible to avoid further inconvenience.</p>
#                     <p>Thank you for choosing Migoo. We value your trust and are committed to providing you with the best service possible.
#                     </p>
#                     <div><b>Thanks & Regards,</b></div>
#                     <div><b>Migoo Equipments</b></div> <br>
#                     <div>
#                         <table>
#                             <tr>
#                                 <td style="border-right: 2.5px solid #e6992a; ">
#                                 <img
#                                     src="https://www.migoo.in/files/logo-w250%20(1).png">
#                                 </td>
#                                 <td style="padding-left:12px; color: black;">
#                                     <div style="display: flex; margin-bottom: 2px;"> <img src="https://www.migoo.in/files/call (1).png"
#                                             height="16px" width="16px" style="margin-top: auto; margin-bottom: auto;">
#                                         <div style="margin-left: 5px;"> +91 79692 12223 </div>
#                                     </div>
#                                     <div style="display: flex; margin-bottom: 2px;"> <img src="https://www.migoo.in/files/email1ead26.png"
#                                             height="16px" width="16px" style="margin-top: auto; margin-bottom: auto;"> <a
#                                             style="color: black;" href="mailto:info@migoo.in" style="text-decoration: none;">
#                                             <div style="margin-left: 5px;">info@migoo.in</div>
#                                         </a> </div>
#                                     <div style="display: flex; margin-bottom: 2px;"> <img src="https://www.migoo.in/files/link.png"
#                                             height="16px" width="16px" style="margin-top: auto; margin-bottom: auto;"> <a
#                                             style="color: black;" href="https://www.migoo.in">
#                                             <div style="margin-left: 5px;">www.migoo.in</div>
#                                         </a> </div>
#                                     <div style="display: flex; margin-bottom: 2px;"> <img src="https://www.migoo.in/files/location.png"
#                                             height="16px" width="16px" style="margin-top: auto; margin-bottom: auto;">
#                                         <div style="margin-left: 5px;">Migved Solutions Private Limited,</div>
#                                     </div>
#                                     <div style="margin-left: 20px;"> A-1204, Mondeal Heights, <br> Iskcon Cross Road, S.G.Highway, <br>
#                                         Ahmedabad-380058 </div>
#                                     <div style="margin-top: 10px;"> <a
#                                             href="https://www.facebook.com/people/Migoo-Equipments/100087829991875/?mibextid=ZbWKwL"
#                                             target="_blank"> <img src="https://www.migoo.in/files/facebook.png" style="height: 20px;"></a>
#                                         <a href="https://www.instagram.com/migoo_equipment/?igshid=YmMyMTA2M2Y%3D"> <img
#                                                 src="https://www.migoo.in/files/instagram.png" style="height: 20px;"></a> <a
#                                             href="https://www.linkedin.com/authwall?trk=bf&trkInfo=AQE3GrOu_soLXAAAAYTnfV7Ak5NhrLNM9IxIvNuvfFL51XjUZjWDRN_WROWhhGDHQfI05HuUk46hX4INHsRvXff6X08bFwXCpC3OG-A7nocY7Rtqb7kN1teuUQMukrXRVO5ai84=&original_referer=&sessionRedirect=https%3A%2F%2Fwww.linkedin.com%2Fin%2Fmigoo-equipments-270563257">
#                                             <img src="https://www.migoo.in/files/linkedin.png" style="height: 20px;"></a> <a
#                                             href="https://twitter.com/MigooEquipments"> <img
#                                                 src="https://www.migoo.in/files/twitter-sign.png" style="height: 20px;"></a>
#                                     </div>
#                                 </td>
#                             </tr>
#                         </table>
#                     </div>

#             <br>
#             <div>

#                 <div style="display: flex; margin-bottom: 2px;">
#                     <img
#                         src="https://lh4.googleusercontent.com/Tg-ugYQdUjAPJTtdSu3Rc8pYT0hONyb7dbg-Z0LN2iYvKbhazcdWIu_Vyn7-m7IIPdU0fd9VwxdDKm90nE6tVaAeQ4_b13OV79O7w9sPJiJP4YOqt2juD4XWgjK4v4E5TmIVuOsY3dDyuQ7p3-B4ndw">
#                     <div style="color: green; margin-left: 5px;">Consider The Environment. Think Before You Print.</div>
#                 </div>
#             </div>
#                 '''                           
#             #     print("\n", supplier_dict, "\n")
#             # return supplier_dict
#             s_name = frappe.db.get_value("Supplier", filters={'name': supplier}, fieldname=["name_of_suppier", "whatsapp_no"])  
#             # print("\n", s_name, "\n")
#             if s_name is None:
#                 continue
#             name_of_supplier = s_name[0]
#             whatsapp_no = s_name[1]

#             file_path = name_of_supplier.replace(" ", "_").lower() + '.pdf'
#             pdf = weasyprint.HTML(string=message).write_pdf()
            
#             with open(file_path, 'wb') as f:
#                 f.write(pdf)
                
#             delete_file(f"/files/{file_path}")
#             save_file_on_filesystem(file_path, content=pdf)

#             # create a new document
#             from frappe.utils import today

#             doc = frappe.get_doc({
#                 'doctype': 'Sent File',
#                 'file_path': file_path,
#                 'sent_date': today()
#             })
#             doc.insert(ignore_permissions=True)
#             frappe.db.commit()

#             template = 'compalince_update_remainders_in_cc'
#             number = whatsapp_no
#             from frappe.utils import get_url
#             site_url = get_url()
#             file_link = site_url + '/files/' + file_path
            
#             if with_reminder == 0:
#                 message_count = get_compliance_template_count(number, template)
#                 if message_count == 0:
#                     lowmtbs.append("whatsapp_message_details", {
#                         "whatsapp_no": number,
#                         "pdf_link": file_link,
#                         "template_name": template,
#                         "supplier_name": name_of_supplier,
#                         "doc_type": "Supplier",
#                         "doc_name": supplier,
#                         "type": "14_days_reminder"
#                     })
#             else:
#                 # send reminder template
#                 whatsapp_no = frappe.db.get_value("Supplier", filters={'name': supplier}, fieldname=["whatsapp_no"])  
#                 if whatsapp_no is None:
#                     continue

#                 message_count = get_compliance_template_count(number, template)
#                 r_message_count = get_compliance_template_count(number, "compliance_update")

#                 if message_count == 0:
#                     if r_message_count == 0:
#                         lowmtbs.append("whatsapp_message_details", {
#                             "whatsapp_no": number,
#                             "pdf_link": file_link,
#                             "template_name": template,
#                             "supplier_name": name_of_supplier,
#                             "doc_type": "Supplier",
#                             "doc_name": supplier,
#                             "type": "14_days_reminder",
#                             "with_reminder": 1
#                         })

#                         from frappe.utils import random_string
#                         wtsw = frappe.new_doc("Wati Webhook Template Sent")
#                         wtsw.whatsapp_no = '91'+whatsapp_no if whatsapp_no else ''
#                         wtsw.template_name = 'compliance_update'
#                         wtsw.doc_type = "Supplier"
#                         wtsw.doc_name = supplier
#                         wtsw.date = add_to_date(datetime.now(), days=7, as_string=True, as_datetime=True)
#                         wtsw.reminder_id = random_string(40)

#                         for equipment in equipment_list:
#                             child_row = wtsw.append("whatsapp_equipment", {})
#                             child_row.equipment_name = equipment["equipment_name"]

#                         wtsw.insert(ignore_permissions=True)
#                         frappe.db.commit()
#                     else:
#                         lowmtbs.append("whatsapp_message_details", {
#                             "whatsapp_no": number,
#                             "pdf_link": file_link,
#                             "template_name": template,
#                             "supplier_name": name_of_supplier,
#                             "doc_type": "Supplier",
#                             "doc_name": supplier,
#                             "type": "14_days_reminder",
#                         })

#         if lowmtbs.whatsapp_message_details:
#             lowmtbs.insert(ignore_permissions=True)
#             frappe.db.commit()
    

# @frappe.whitelist(allow_guest=True)
# def send_messages_from_list_of_reminder(name=""):
#     if frappe.db.get_single_value('WhatsApp Api', 'disabled'):
#         return frappe.msgprint('Your WhatsApp api key is not set or may be disabled')

#     access_token, api_endpoint, name_type, version = whatsapp_keys_details()
#     headers = {
#         "Content-Type": "text/json",
#         "Authorization": access_token
#     }
    
#     lowmtbs = frappe.get_doc("List of WhatsApp Messages to be Sent", name)
    
#     # whatsapp_details = lowmtbs.whatsapp_message_details
#     if lowmtbs.sent == 0 and lowmtbs.is_reminder == 0:
#         reminder_list = []
#         sent_wp_no = []
#         for wmd in lowmtbs.whatsapp_message_details:
#             if wmd.type == "14_days_reminder" and wmd.whatsapp_no not in sent_wp_no:
#                 payload = {
#                     "broadcast_name": wmd.template_name,
#                     "template_name": wmd.template_name,
#                     "parameters": [
#                         {
#                             "name": "supp_name",
#                             "value": wmd.supplier_name
#                         },
#                         {
#                             "name": "pdf_link",
#                             "value": wmd.pdf_link
#                         }
#                     ],
#                 }

#                 test = frappe.new_doc("testing")
#                 test.number = wmd.whatsapp_no
#                 test.template_name = wmd.template_name
#                 test.insert(ignore_permissions=True)
#                 frappe.db.commit()
                
#                 url = f"{api_endpoint}/{name_type}/{version}/sendTemplateMessage?whatsappNumber=91{wmd.whatsapp_no}"
#                 response = requests.post(url, json=payload, headers=headers)
#                 data = json.loads(response.text)

#                 if "result" in data and data["result"]:
#                     log = frappe.new_doc("Whatsapp Message Daily Limit Log")
#                     log.whatsapp_no = wmd.whatsapp_no
#                     log.template_name = wmd.template_name
#                     log.insert()
#                     frappe.db.commit()

#                     wmcl = frappe.new_doc("Whatsapp Message Compliance Log")
#                     wmcl.whatsapp_no = wmd.whatsapp_no
#                     wmcl.template_name = wmd.template_name
#                     wmcl.sent_date = today()
#                     wmcl.insert(ignore_permissions=True)

#                     # set comment whatsapp message sent
#                     # comment(wmd.whatsapp_no, template_name=wmd.template_name, bt=[
#                     #     {
#                     #         "name": "supp_name",
#                     #         "value": wmd.supplier_name
#                     #     },
#                     #     {
#                     #         "name": "pdf_link",
#                     #         "value": wmd.pdf_link
#                     #     }
#                     # ])

#                     from whatsapp_app.api import set_comment
#                     content = f"<div class='card'><b style='color: green' class='px-2 pt-2'>Whatsapp Compliance Template Sent: </b> <a href='{wmd.pdf_link}' class='px-2 pb-2'>{wmd.pdf_link}</span></div>"
#                     set_comment("Supplier", wmd.doc_name, "Administrator", content)

#                 sent_wp_no.append(wmd.whatsapp_no)

#             if wmd.with_reminder == 1:
#                 reminder_list.append(wmd.whatsapp_no)
#                 sleep(2)


#         for number in frappe.utils.unique(reminder_list):
#             payload = {
#                     "broadcast_name": "compliance_update",
#                     "template_name": "compliance_update",
#                     "parameters": [],
#                 }

#             url = f"{api_endpoint}/{name_type}/{version}/sendTemplateMessage?whatsappNumber=91{number}"
#             response = requests.post(url, json=payload, headers=headers)
#             if "result" in data and data["result"]:
#                 log = frappe.new_doc("Whatsapp Message Daily Limit Log")
#                 log.whatsapp_no = number
#                 log.template_name = "compliance_update"
#                 log.insert()
#                 frappe.db.commit()

#                 wmcl = frappe.new_doc("Whatsapp Message Compliance Log")
#                 wmcl.whatsapp_no = number
#                 wmcl.template_name = "compliance_update"
#                 wmcl.sent_date = today()
#                 wmcl.insert(ignore_permissions=True)

#                 # # set comment whatsapp message sent
#                 # from whatsapp_app.api import set_comment
#                 # content = f"<div class='card'><b style='color: green' class='px-2 pt-2'>Whatsapp Reminder Template Sent: </b> <span class='px-2 pb-2'>{wmd.pdf_link}</span></div>"
#                 # set_comment("Supplier", wmd.doc_name, "Administrator", content)

#             test = frappe.new_doc("testing")
#             test.number = number
#             test.template_name = "compliance_update"
#             test.insert(ignore_permissions=True)
#             frappe.db.commit()

#         lowmtbs.sent = 1
#         lowmtbs.sent_date = today()
#         lowmtbs.sent_by = frappe.session.user
#         lowmtbs.save()
#         frappe.db.commit()

#     elif lowmtbs.sent == 0 and lowmtbs.is_reminder == 1:
#         sent_r_wp_no = []
#         for wmd in lowmtbs.whatsapp_message_details:
#             if wmd.whatsapp_no not in sent_r_wp_no:
#                 url = f"{api_endpoint}/{name_type}/{version}/sendTemplateMessage?whatsappNumber={wmd.whatsapp_no}"
#                 payload = {
#                     "broadcast_name": "compliance_update",
#                     "template_name": "compliance_update",
#                     "parameters": []
#                 }
                
#                 response = requests.post(url, json=payload, headers=headers)
#                 data = json.loads(response.text)

#                 if "result" in data and data["result"]:
#                     log = frappe.new_doc("Whatsapp Message Daily Limit Log")
#                     log.whatsapp_no = wmd.whatsapp_no
#                     log.template_name = "compliance_update"
#                     log.insert()
#                     frappe.db.commit()

#                     wmcl = frappe.new_doc("Whatsapp Message Compliance Log")
#                     wmcl.whatsapp_no = wmd.whatsapp_no
#                     wmcl.template_name = "compliance_update"
#                     wmcl.sent_date = today()
#                     wmcl.insert(ignore_permissions=True)
                
#                 sent_r_wp_no.append(wmd.whatsapp_no)
#                 test = frappe.new_doc("testing")
#                 test.number = wmd.whatsapp_no
#                 test.template_name = "compliance_update"
#                 test.insert(ignore_permissions=True)
#                 frappe.db.commit()

#         lowmtbs.sent = 1
#         lowmtbs.sent_date = today()
#         lowmtbs.sent_by = frappe.session.user
#         lowmtbs.save()
#         frappe.db.commit()


#     # send report to migoo managment
#     from frappe.utils import get_url
#     # numbers = ['8401265878', '7990915950', '9313086301', '9724547104', '8347718490', '9886107360', '9708618353', '9898019009']
#     numbers = ['9886107360', '9724547104', '9313086301', '7990915950', '8401265878']
#     report = f"{get_url()}/api/method/frappe.utils.print_format.download_pdf?doctype=List%20of%20WhatsApp%20Messages%20to%20be%20Sent&name={name}"
#     payload = {
#                 "broadcast_name": "sent_pdf",
#                 "template_name": "sent_pdf",
#                 "parameters": [{
#                             "name": "pdf_link",
#                             "value": f"{report}"
#                         },
#                         {
#                             "name": "doctype_name",
#                             "value": "equipment reminder whatsapp list report"
#                         }],
#             }
#     for number in numbers:

#         url = f"{api_endpoint}/{name_type}/{version}/sendTemplateMessage?whatsappNumber=91{number}"
#         response = requests.post(url, json=payload, headers=headers)
       
#         test = frappe.new_doc("testing")
#         test.number = number
#         test.template_name = "sent_pdf"
#         test.insert(ignore_permissions=True)
#         frappe.db.commit()


############################## send again message if not answer was received #############################

# @frappe.whitelist(allow_guest=True)
# def send_remider_if_not_repliyed():
#     # scheduler event
#     enable_cron = frappe.db.get_single_value('Custom Settings', 'enable_cron_job')
#     if enable_cron == 1:
#         if frappe.db.get_single_value('WhatsApp Api', 'disabled'):
#                 return 'Your WhatsApp api key is not set or may be disabled'

#         # data = frappe.db.get_list("Wati Webhook Template Sent", filters=[["date", "=", frappe.utils.add_days(frappe.utils.now_datetime(), -6)], ["replied_text", "in", ["No", "whatsapp_no"]]], fields=["name", "whatsapp_no", "doc_type", "doc_name", "template_name"])
#         data = frappe.db.get_list("Wati Webhook Template Sent", filters=[["date", "=", frappe.utils.add_days(frappe.utils.now_datetime(), -3)], ["replied_text", "in", ["No", ""]]], fields=["name", "whatsapp_no", "doc_type", "doc_name", "template_name", "reminder_id"])
#         lowmtbs = frappe.new_doc("List of WhatsApp Messages to be Sent")
#         lowmtbs.is_reminder = 1
#         r_whatsapp = []
#         for i in data:
#             check = frappe.db.count("Wati Webhook Template Sent", {"reminder_id": i.reminder_id})
#             if check <= 3:
#                 equipments = frappe.db.get_list("Whatsapp Equipment", {"parent": i.name}, ["equipment_name"])
                
#                 if i.whatsapp_no not in r_whatsapp:
#                     lowmtbs.append("whatsapp_message_details", {
#                         "whatsapp_no": i.whatsapp_no[-10:],
#                         "template_name": "compliance_update",
#                         "supplier_name": i.doc_name,
#                         "doc_type": "Supplier",
#                         "doc_name": i.doc_name,
#                     })
#                     r_whatsapp.append(i.whatsapp_no)


#                 wtsw = frappe.new_doc("Wati Webhook Template Sent")
#                 wtsw.whatsapp_no = i.whatsapp_no if i.whatsapp_no else ''
#                 wtsw.template_name = 'compliance_update'
#                 wtsw.doc_type = i.doc_type
#                 wtsw.doc_name = i.doc_name
#                 wtsw.date = today()
#                 wtsw.reminder_id = i.reminder_id
#                 for equipment in equipments:
#                     child_row = wtsw.append("whatsapp_equipment", {})
#                     child_row.equipment_name = equipment["equipment_name"]

#                 wtsw.insert(ignore_permissions=True)
#                 frappe.db.commit()
#         if lowmtbs.whatsapp_message_details:
#             lowmtbs.insert(ignore_permissions=True)
#             frappe.db.commit()


#####################  send reminder message from list using scheduler ###################################

@frappe.whitelist(allow_guest=True)
def send_whatsapp_reminder_using_scheduler():
    enable_cron = frappe.db.get_single_value('Custom Settings', 'enable_cron_job')
    if enable_cron == 1:
        names = frappe.db.get_list("List of WhatsApp Messages to be Sent", filters={"date": today(), "sent": 0}, fields=["name"], pluck='name')
        for name in names:
            send_messages_from_list_of_reminder(name)


#### new compliance change code after dec meeting remove yes/no template. ####
            
import frappe
from frappe.utils import nowdate, formatdate, nowtime
from datetime import datetime, timedelta
from collections import defaultdict
import requests


@frappe.whitelist()
def send_insurance_whatsapp():
    enable_cron = frappe.db.get_single_value('Custom Settings', 'enable_cron_job')
    if enable_cron == 1:
        name = frappe.db.sql(
        """
        WITH CTE AS (
            SELECT
                name,
                supplier,
                supplier_email,
                whatsapp_no,
                supplier_name,
                equipment_main_category,
                register_no,
                CASE
                    WHEN rto_register = 'Registered' THEN model
                    ELSE equipment_model_no
                END AS "model",
                insurance_date AS 'date',
                DATEDIFF(insurance_date, CURDATE()) AS 'daysToGo',
                'Insurance' AS 'type'
            FROM
                tabItem
            WHERE
                insurance_date >= CURDATE()
                AND DATEDIFF(insurance_date, CURDATE()) <= 15

            UNION ALL

            SELECT
                name,
                supplier,
                supplier_email,
                whatsapp_no,
                supplier_name,
                equipment_main_category,
                register_no,
                CASE
                    WHEN rto_register = 'Registered' THEN model
                    ELSE equipment_model_no
                END AS "model",
                fitness_dt AS 'date',
                DATEDIFF(fitness_dt, CURDATE()) AS 'daysToGo',
                'Fitness' AS 'type'
            FROM
                tabItem
            WHERE
                fitness_dt >= CURDATE()
                AND DATEDIFF(fitness_dt, CURDATE()) <= 15

            UNION ALL

            SELECT
                name,
                supplier,
                supplier_email,
                whatsapp_no,
                supplier_name,
                equipment_main_category,
                register_no,
                CASE
                    WHEN rto_register = 'Registered' THEN model
                    ELSE equipment_model_no
                END AS "model",
                pollution AS 'date',
                DATEDIFF(pollution, CURDATE()) AS 'daysToGo',
                'Pollution' AS 'type'
            FROM
                tabItem
            WHERE
                pollution >= CURDATE()
                AND DATEDIFF(pollution, CURDATE()) <= 15

            UNION ALL 

            SELECT 
                equipment_id,
                cl.supplier,
                cl.supplier_email,
                whatsapp_no,
                cl.supplier_name,
                cld.equipment_sub_category,
                equipment_no as register_no,
                CASE
                    WHEN rto_register = 'Registered' THEN model
                    ELSE equipment_model_no
                END AS "model",
                valid_till AS 'date',
                DATEDIFF(valid_till, CURDATE()) AS 'daysToGo',
                compliance_type AS 'type'
            FROM `tabCompliance Log Detail` cld
            INNER JOIN `tabItem` i ON i.name = cld.equipment_id
            INNER JOIN `tabCompliance Log` cl ON cl.name = cld.parent
            WHERE valid_till = DATE_SUB(CURDATE(), INTERVAL (DAYOFWEEK(CURDATE()) + 5) % 7 DAY)
        )

        SELECT
            name,
            supplier,
            supplier_email,
            supplier_name,
            equipment_main_category,
            register_no,
            model,
            DATE_FORMAT(date, '%d-%m-%Y') AS 'date',
            type,
            daysToGo,
            whatsapp_no
        FROM
            CTE
        GROUP BY type, date, register_no
        ORDER BY supplier,
        DATE(date) asc;

   """
    )
       

        supplier_dict = defaultdict(list)

        equipment_ids = []

        for i in name:
            equipment_name = i[0]
            supplier = i[1]
            supplier_email = i[2]
            supplier_name = i[3]
            equipment_main_category = i[4]
            register_no = i[5]
            model = i[6]
            date = i[7]
            status = i[8]
            daystogo = i[9]
            whatsapp_no = i[10]
            equipment_ids.append(i[0])


            supplier_dict[supplier].append(
                {
                    "equipment_name": equipment_name,
                    "supplier_email": supplier_email,
                    "supplier_name": supplier_name,
                    "equipment_main_category": equipment_main_category,
                    "register_no": register_no,
                    "model": model,
                    "date": date,
                    "status": status,
                    "daystogo": daystogo,
                    "supplier": supplier,
                    "whatsapp_no": whatsapp_no
                }
            )

        lowmtbs = frappe.new_doc("List of WhatsApp Messages to be Sent")

        for supplier, equipment_list in supplier_dict.items():

            # message = """
            #     <div>
            #         <div class="sec-2">
            #             <h3 style="">Hello, {}</h4>
            #             <p>We hope this message finds you well. We are writing to remind you that your Equipment's documents are set to expire. The details are mentioned below.</p>
            #             <table border=1px cellspacing="0" cellpadding="4";>
            #                 <tr style="background-color: #e6992a;">
            #                     <th>Compliance</th>
            #                     <th>Valid Till</th>
            #                     <th>Expiring in</th>
            #                     <th>Equipment</th>
            #                     <th>Equipment No</th>
            #                     <th>Model No</th>
            #                 </tr>
            #     """.format(
            #     supplier_dict[supplier][0]["supplier_name"]
            # )

            supp_data = get_supplier_or_company_name(supplier_dict[supplier][0]['supplier'])
            supplier_name = supp_data['supplier_name']
            is_company = supp_data["is_company"]

            header_image_url = "https://www.migoo.in/files/migoo-logo-black-high.png"
            footer_image_url = get_footer_advertisement_url()

            css = f"""
            <style>
                @page {{
                    size: A4 portrait;
                    margin-top: 6em;
                    margin-bottom: 16em;
                    margin-left: 3em;
                    margin-right: 3em;
                    
                    @top-right {{
                        width: 100%;
                        height: 70px;
                        left: 50;
                        right: 0;
                        background-position: right;
                        content: "";
                        background-image: url({header_image_url}); 
                        background-size: contain; 
                        background-repeat: no-repeat; 
                    }}

                    @bottom-center {{
                        width: 100%;
                        height: 95%;
                        left: 0;
                        right: 0;
                        content: "";
                        background-image: url({footer_image_url});
                        background-size: 100% 100%; /* This will cover the entire width and height while maintaining aspect ratio */
                        background-repeat: no-repeat;
                    }}
                }}
            
                body {{
                    margin: 0; /* Remove the body margin to avoid additional space */
                }}

            </style>                
            """

            message = f"""
                    <!DOCTYPE html>
                    <html>
                    <head>
                        <title>{supplier_name}</title>
                    
                        {css}
                        
                        </style>
                    </head>
                    <body>
                
            """

            message += '''
                    <div>
                        <div class="sec-2">
                            <h3 style="">Hello, {}</h4>
                        <p>We hope this message finds you well. We are writing to remind you that your Equipment's documents are set to expire. The details are mentioned below.</p>
                            <table border="1px" cellspacing="0" cellpadding="4" style="border-collapse: collapse;">
                                <tr style="background-color: #e6992a;">
                                    <th style="border: 1px solid black; padding: 4px;">Compliance</th>
                                    <th style="border: 1px solid black; padding: 4px;">Valid Till</th>
                                    <th style="border: 1px solid black; padding: 4px;">Expiring in</th>
                                    <th style="border: 1px solid black; padding: 4px;">Equipment</th>
                                    <th style="border: 1px solid black; padding: 4px;">Equipment No</th>
                                    <th style="border: 1px solid black; padding: 4px;">Model No</th>
                                </tr>
                    '''.format(supplier_name)

            for equipment in equipment_list:
                
                message += """
                            <tr>
                                    <td style="border: 1px solid black; padding: 4px; text-align: center;">{}</td>
                                    <td style="border: 1px solid black; padding: 4px; text-align: center;">{}</td>
                                    <td style="border: 1px solid black; padding: 4px; text-align: center; background-color: {}">{} Days to Go</td>
                                    <td style="border: 1px solid black; padding: 4px; text-align: center;">{}</td>
                                    <td style="border: 1px solid black; padding: 4px; text-align: center;">{}</td>
                                    <td style="border: 1px solid black; padding: 4px; text-align: center; font-size: 12px;">{}</td>
                            </tr>                           
                                
                """.format(
                    equipment["status"],
                    equipment["date"],
                    get_row_background_color(equipment["daystogo"]),
                    equipment["daystogo"],
                    equipment["equipment_main_category"],
                    equipment["register_no"],
                    equipment["model"],
                )


            message += '''
                        </table>
                    </div>
                </div>
                <div>
                        <p>Get it renewed as soon as possible to avoid further inconvenience.</p>
                        <p>Thank you for choosing Migoo. We value your trust and are committed to providing you with the best service possible.
                        </p>
                        <div><b>Thanks & Regards,</b></div>
                        <div><b>Migoo Equipments</b></div> <br>
                        <div>
                            <table>
                                <tr>
                                    <td style="border-right: 2.5px solid #e6992a; ">
                                    <img
                                        src="https://www.migoo.in/files/logo-w250%20(1).png">
                                    </td>
                                    <td style="padding-left:12px; color: black;">
                                        <div style="display: flex; margin-bottom: 2px;"> <img src="https://www.migoo.in/files/call (1).png"
                                                height="16px" width="16px" style="margin-top: auto; margin-bottom: auto;">
                                            <div style="margin-left: 5px;"> +91 79692 12223 <br> +91 98255 32427</div>
                                        </div>
                                        
                                        <div style="display: flex; margin-bottom: 2px;"> <img src="https://www.migoo.in/files/email1ead26.png"
                                                height="16px" width="16px" style="margin-top: auto; margin-bottom: auto;"> <a
                                                style="color: black;" href="mailto:info@migoo.in" style="text-decoration: none;">
                                                <div style="margin-left: 5px;">info@migoo.in</div>
                                            </a> </div>
                                        <div style="display: flex; margin-bottom: 2px;"> <img src="https://www.migoo.in/files/link.png"
                                                height="16px" width="16px" style="margin-top: auto; margin-bottom: auto;"> <a
                                                style="color: black;" href="https://www.migoo.in">
                                                <div style="margin-left: 5px;">www.migoo.in</div>
                                            </a> </div>
                                        <div style="display: flex; margin-bottom: 2px;"> <img src="https://www.migoo.in/files/location.png"
                                                height="16px" width="16px" style="margin-top: auto; margin-bottom: auto;">
                                            <div style="margin-left: 5px;">Migved Solutions Private Limited,</div>
                                        </div>
                                        <div style="margin-left: 20px;"> A-1204, Mondeal Heights, <br> Iskcon Cross Road, S.G.Highway, <br>
                                            Ahmedabad-380058 </div>
                                        <div style="margin-top: 10px;"> <a
                                                href="https://www.facebook.com/people/Migoo-Equipments/100087829991875/?mibextid=ZbWKwL"
                                                target="_blank"> <img src="https://www.migoo.in/files/facebook.png" style="height: 20px;"></a>
                                            <a href="https://www.instagram.com/migoo_equipment/?igshid=YmMyMTA2M2Y%3D"> <img
                                                    src="https://www.migoo.in/files/instagram.png" style="height: 20px;"></a> <a
                                                href="https://www.linkedin.com/authwall?trk=bf&trkInfo=AQE3GrOu_soLXAAAAYTnfV7Ak5NhrLNM9IxIvNuvfFL51XjUZjWDRN_WROWhhGDHQfI05HuUk46hX4INHsRvXff6X08bFwXCpC3OG-A7nocY7Rtqb7kN1teuUQMukrXRVO5ai84=&original_referer=&sessionRedirect=https%3A%2F%2Fwww.linkedin.com%2Fin%2Fmigoo-equipments-270563257">
                                                <img src="https://www.migoo.in/files/linkedin.png" style="height: 20px;"></a> <a
                                                href="https://twitter.com/MigooEquipments"> <img
                                                    src="https://www.migoo.in/files/twitter-sign.png" style="height: 20px;"></a>
                                        </div>
                                    </td>
                                </tr>
                            </table>
                        </div>

                <br>
                <div>

                    <div style="display: flex; margin-bottom: 2px;">
                        <img
                            src="https://lh4.googleusercontent.com/Tg-ugYQdUjAPJTtdSu3Rc8pYT0hONyb7dbg-Z0LN2iYvKbhazcdWIu_Vyn7-m7IIPdU0fd9VwxdDKm90nE6tVaAeQ4_b13OV79O7w9sPJiJP4YOqt2juD4XWgjK4v4E5TmIVuOsY3dDyuQ7p3-B4ndw">
                        <div style="color: green; margin-left: 5px;">Consider The Environment. Think Before You Print.</div>
                    </div>
                </div>
                </div>
                </body>
                </html>
                    '''  
            
        
            # print("\n\n message", message, "\n\n")
            # return message

            if supplier_dict[supplier][0]["supplier_name"]:
                file_path = supplier_name.replace(" ", "_").lower() + '.pdf'
                pdf = weasyprint.HTML(string=message).write_pdf()
                
                with open(file_path, 'wb') as f:
                    f.write(pdf)
                    
                delete_file(f"/files/{file_path}")
                save_file_on_filesystem(file_path, content=pdf)

                # create a new document
                from frappe.utils import today

                doc = frappe.get_doc({
                    'doctype': 'Sent File',
                    'file_path': file_path,
                    'sent_date': today()
                })
                doc.insert(ignore_permissions=True)
                frappe.db.commit()


                from frappe.utils import get_url
                site_url = get_url()
                file_link = site_url + '/files/' + file_path

                supplier = supplier_dict[supplier][0]["supplier"]
                whatsapp_no = supplier_dict[supplier][0]["whatsapp_no"]
                template = "compalince_update_remainders_in_cc"
                
                if check_daily_message_limit_for_user(whatsapp_no, "compalince_update_remainders_in_cc"):
                    lowmtbs.append("whatsapp_message_details", {
                        "whatsapp_no": whatsapp_no,
                        "pdf_link": file_link,
                        "template_name": template,
                        "supplier_name": supplier_name,
                        "doc_type": "Supplier",
                        "doc_name": supplier,
                        "is_company": is_company
                    })

        lowmtbs.insert(ignore_permissions=True)
        frappe.db.commit()
        # send_whatsapp_reminder_using_scheduler()


@frappe.whitelist(allow_guest=True)
def send_messages_from_list_of_reminder(name=""):
    if frappe.db.get_single_value('WhatsApp Api', 'disabled'):
        return frappe.msgprint('Your WhatsApp api key is not set or may be disabled')

    access_token, api_endpoint, name_type, version = whatsapp_keys_details()
    headers = {
        "Content-Type": "text/json",
        "Authorization": access_token
    }
    
    lowmtbs = frappe.get_doc("List of WhatsApp Messages to be Sent", name)
    
    # whatsapp_details = lowmtbs.whatsapp_message_details
    if lowmtbs.sent == 0:
        sent_wp_no = []
        for wmd in lowmtbs.whatsapp_message_details:
            if wmd.whatsapp_no not in sent_wp_no:
                if check_daily_message_limit_for_user(wmd.whatsapp_no, "compalince_update_remainders_in_cc"):
                    
                    payload = {
                        "broadcast_name": wmd.template_name,
                        "template_name": wmd.template_name,
                        "parameters": [
                            {
                                "name": "supp_name",
                                "value": wmd.supplier_name
                            },
                            {
                                "name": "pdf_link",
                                "value": wmd.pdf_link
                            }
                        ],
                    }

                    test = frappe.new_doc("testing")
                    test.number = wmd.whatsapp_no
                    test.template_name = wmd.template_name
                    test.insert(ignore_permissions=True)
                    frappe.db.commit()
                    
                    url = f"{api_endpoint}/{name_type}/{version}/sendTemplateMessage?whatsappNumber=91{wmd.whatsapp_no}"
                    response = requests.post(url, json=payload, headers=headers)
                    data = json.loads(response.text)

                    # if "result" in data and data["result"]:
                    # # tab start
                    #     log = frappe.new_doc("Whatsapp Message Daily Limit Log")
                    #     log.whatsapp_no = wmd.whatsapp_no
                    #     log.template_name = wmd.template_name
                    #     log.insert()
                    #     frappe.db.commit()

                    #     from whatsapp_app.api import set_comment
                    #     content = f"<div class='card'><b style='color: green' class='px-2 pt-2'>Whatsapp Compliance Template Sent: </b> <a href='{wmd.pdf_link}' class='px-2 pb-2'>{wmd.pdf_link}</span></div>"
                    #     set_comment("Supplier", wmd.doc_name, "Administrator", content)
                    # # tab end

                    sent_wp_no.append(wmd.whatsapp_no)

        lowmtbs.sent = 1
        lowmtbs.sent_date = today()
        lowmtbs.sent_by = frappe.session.user
        lowmtbs.save()
        frappe.db.commit()


    # # send report to migoo managment
    # from frappe.utils import get_url
    # # numbers = ['8401265878', '7990915950', '9313086301', '9724547104', '8347718490', '9886107360', '9708618353', '9898019009']
    # numbers = ['9886107360', '9724547104', '9313086301', '7990915950', '8401265878']
    # report = f"{get_url()}/api/method/frappe.utils.print_format.download_pdf?doctype=List%20of%20WhatsApp%20Messages%20to%20be%20Sent&name={name}"
    # payload = {
    #             "broadcast_name": "sent_pdf",
    #             "template_name": "sent_pdf",
    #             "parameters": [{
    #                         "name": "pdf_link",
    #                         "value": f"{report}"
    #                     },
    #                     {
    #                         "name": "doctype_name",
    #                         "value": "equipment reminder whatsapp list report"
    #                     }],
    #         }
    # for number in numbers:

    #     url = f"{api_endpoint}/{name_type}/{version}/sendTemplateMessage?whatsappNumber=91{number}"
    #     response = requests.post(url, json=payload, headers=headers)
       
    #     test = frappe.new_doc("testing")
    #     test.number = number
    #     test.template_name = "sent_pdf"
    #     test.insert(ignore_permissions=True)
    #     frappe.db.commit()
        
        
def get_row_background_color(days_to_go):
    try:
        days_to_go = int(days_to_go)
        if days_to_go <= 00:
            return "#FF0000"
        elif days_to_go <= 7:
            return "#FFA500"
        else:
            return "green"
    except ValueError:
        return "#FFFFFF"
    
def get_footer_advertisement_url():
    enable = frappe.db.get_single_value("Advertisement", "enable")
    if enable == 1:
        from frappe.utils import get_url 
        url = get_url() + frappe.db.get_single_value("Advertisement", "advertisement_image")
        print("\n\n url", url)
        return url.replace(' ', '%20')
    else:
        return ""
    

def get_supplier_or_company_name(supplier):
    if supplier:
        doc = frappe.get_doc("Supplier", supplier)
    
        if doc.supplier_type == "Company":
            return {"supplier_name": doc.company_name, "is_company": 1}
        else:
            return {"supplier_name": doc.name_of_suppier, "is_company": 0}