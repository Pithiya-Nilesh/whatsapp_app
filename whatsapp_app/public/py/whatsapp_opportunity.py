import frappe
import json
from frappe import _
import requests
import re


def get_the_template():    
    # Get all templates with name 'opportunity_alert_to_sales_person'
    templates = str(frappe.db.sql(" select sample from `tabTemplates` where name=%s ", ('opportunity_alert_to_sales_person'), as_dict=True))
      
    # SETTING THE PATTERN TO GET THE FIELD OF THE TEMPLATE MESSAGE
    pattern = r"{{(.*?)}}"

    # MAKE THE LIST OF THE FIELD
    matches = re.findall(pattern, templates)    

    return matches

@frappe.whitelist(allow_guest=True)
def whatsapp_message_send_opportunity(allocated_to, reference_name):    
    # if doc.reference_type == "Opportunity" and doc.status == "Open":
        print("\n\n", allocated_to)
        user_details = frappe.db.sql("select mobile_no,full_name from `tabUser` where name=%s ", (allocated_to), as_dict=True)      
        print("\n\n\n", user_details, "\n")
        whatsapp_settings = frappe.db.sql(" select field,value from `tabSingles` where doctype=%s", ("WhatsApp Api"), as_dict=True)
        
        for user in user_details:                       
            # SETTING THE HEADERS FOR THE API
            headers = {"Content-Type": "text/json", "Authorization": whatsapp_settings[0].value}                      

            # # URL OF THE API
            url = f"{whatsapp_settings[2].value}/{whatsapp_settings[11].value}/{whatsapp_settings[14].value}/sendTemplateMessage?whatsappNumber=91{user.mobile_no}"
            
            field_value = frappe.db.sql(" select custom_opportunity_name, industry, contact_mobile,contact_email,custom_equipment_name,request_type  from `tabOpportunity` where name=%s",reference_name)  
    
            new_list = field_value[0][:1] + (user.full_name,) + field_value[0][1:]

            new_tuple = get_the_template()

            # Create a list of dictionaries
            json_data = []

            # Iterate over the tuple and keys simultaneously
            for value, key in zip(new_list, new_tuple):
                # Replace None values with "-"
                if value is None:
                    value = "-"
                # Create a dictionary for the parameter
                parameter = {
                    "name": key,
                    "value": value
                }
                # Append the dictionary to the list
                json_data.append(parameter)

            template = "opportunity_alert_to_sales_person"
            # # SET THE PAYLOAD DATA FOR THE API JSON PAYLOAD
            payload = {
                "parameters": json_data,
                "broadcast_name": template,
                "template_name": template,
            } 

            # # SEND WHATSAPP MESSAGE POST REQUEST
            response = requests.post(url, json=payload, headers=headers)  
            set_data_in_wati_call_log(user.mobile_no, response)            
            comment(field_value[0][2], template, json_data)


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
def comment(number,template, message, bt='', bt1=''):
    if bt1:
        bt = json.loads(bt1)
    name = frappe.session.user    
    o_name = frappe.db.get_value('Opportunity', filters={"contact_mobile": number}, fieldname=["name"])    
    
    if message != '':
        sample = frappe.db.get_value("Templates", filters={'template_name': template}, fieldname=["sample"])       
        formatted_text = sample
        for item in message:
            formatted_text = formatted_text.replace('{{' + item['name'] + '}}', item['value'])
        
        content = f"<div class='card'><b style='color: green' class='px-2 pt-2'>Whatsapp Message Sent: </b> <span class='px-2 pb-2'>{formatted_text}</span></div>"
    else:
        sample = frappe.db.get_value("Templates", filters={'template_name': template}, fieldname=["sample"])
        for item in message:
            formatted_text = formatted_text.replace('{{' + item['name'] + '}}', item['value'])
        
        content = f"<div class='card'><b style='color: green' class='px-2 pt-2'><i class='fa fa-whatsapp' aria-hidden='true'> Whatsapp Template Sent: </i></b> <a href='/app/templates/{template}' class='px-2 pb-2'>{formatted_text}</a></div>"

    if o_name:
        set_comment('Opportunity', o_name, name, content)
    
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
