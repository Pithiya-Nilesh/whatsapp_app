import datetime
import json
import sys
from frappe.utils import now, getdate
import frappe
import requests
from frappe.model.document import Document
from frappe.utils import add_to_date


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
@frappe.whitelist()
def send_messages(l_mobile=0, template='', l_name='', ):
    if frappe.db.get_single_value('WhatsApp Api', 'disabled'):
        return 'Your WhatsApp api key is not set or may be disabled'
    if l_name:
        l_mobile = frappe.db.get_value("Lead", f"{l_name}", "phone")

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
def send_whatsapp_message(number, message='', template_name=''):
    # number = int(number)
    if frappe.db.get_single_value('WhatsApp Api', 'disabled'):
        return 'Your WhatsApp api key is not set or may be disabled'
    access_token, api_endpoint, name_type, version = whatsapp_keys_details()
    headers = {
        "Content-Type": "text/json",
        "Authorization": access_token
    }
    template_name1 = frappe.db.get_value("Templates", template_name, "template_name")
    url = f"{api_endpoint}/{name_type}/{version}/sendTemplateMessage?whatsappNumber=91{number}"
    if template_name1 != None:
        doctype = frappe.db.get_value("Templates", template_name, ['template_doctype'])
        bt = bulk_templates(template=template_name, l_mobile=number, doctype=doctype)
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
def get_template_list():
    return frappe.db.get_list("Templates", filters={"status": "APPROVED"}, pluck = "name")


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
def send_bulk_whatsapp_message(template_name, doctype, name):
    if frappe.db.get_single_value('WhatsApp Api', 'disabled'):
        return 'Your WhatsApp api key is not set or may be disabled'
    name = json.loads(name)
    template_name1 = frappe.db.get_value("Templates", template_name, "template_name")
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
            print("\n\n template1", template_name1, "\n\n")
            bt = bulk_templates(template=template_name, l_mobile=mobile, doctype=doctype)
            print("\n\n bt", bt, "\n\n")
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
            element_name = template["elementName"]
            status = template["status"]
            body = template["bodyOriginal"]
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
                new_template.insert(ignore_permissions=True)
                frappe.db.commit()
        
        if all_templates_available:
            frappe.msgprint("All templates are available.")
        else:
            None

@frappe.whitelist(allow_guest = True)
def get_template_sample(selected_template, selected_doctype, whatsapp_no):
    list = bulk_templates(template=selected_template, doctype=selected_doctype, l_mobile=whatsapp_no)
    content = get_content(selected_template, list)
    return content

def get_content(template_name='', bt=''):
    if template_name == '':
        return None
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
        content = f"{formatted}"
        return content