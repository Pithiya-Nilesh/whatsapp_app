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
    value2 = frappe.db.sql("""SELECT p.name_in_doctype  FROM `tabParameters`p INNER JOIN `tabTemplates`t ON p.parent = %(name)s and t.name = %(name)s;""",values=values)
    value2_n = frappe.db.sql("""SELECT p.name_in_wati  FROM `tabParameters`p INNER JOIN `tabTemplates`t ON p.parent = %(name)s and t.name = %(name)s;""",values=values)
    value_v=[]
    if len(value2)>0:
        for i in value2:
            for i1 in i:
                value_v.append(i1)
                # print(i1)
    else:
        value_v=["value"]

    value_n=[]
    if len(value2_n)>0:
        for i in value2_n:
            for i1 in i:
                value_n.append(i1)
                # print(i1)
    else:
        value_n=["name"]
    
    final_values =[]
    for i in value_v:
        # print(i)
        if i == 'value':
            print("Terminate")
            final_values.append('value')
        else:
            if i == 'lead_name':
                f=int(l_mobile)
                print(f)
                print(type(f))
                values = {'name': f }
                v = frappe.db.sql("""select lead_name from `tabLead` where mobile_no= %(name)s;""", values=values)
                print("This is lead_name")
                print(v)
                v1 = v[0]
                v2 = v1[0]
                print(v2)
                final_values.append(v2)
            if i == 'company':
                f=int(l_mobile)
                values = {'name': f }
                v = frappe.db.sql("""select company from `tabLead` where mobile_no= %(name)s;""", values=values)
                print("This is company")
                v1 = v[0]
                v2 = v1[0]
                print(v)
                final_values.append(v2)
                # print("welcome")
            if i == 'company_name':
                f=int(l_mobile)
                values = {'name': f }
                v = frappe.db.sql("""select company_name from `tabLead` where mobile_no= %(name)s;""", values=values)
                print("This is company_name")
                v1 = v[0]
                v2 = v1[0]
                print(v)
                final_values.append(v2)
            if i == 'territory':
                f=int(l_mobile)
                values = {'name': f }
                v = frappe.db.sql("""select territory from `tabLead` where mobile_no= %(name)s;""", values=values)
                print("This is territory")
                v1 = v[0]
                v2 = v1[0]
                print(v)
                final_values.append(v2)
            if i == 'source':
                f=int(l_mobile)
                values = {'name': f }
                v = frappe.db.sql("""select source from `tabLead` where mobile_no= %(name)s;""", values=values)
                print("This is source")
                v1 = v[0]
                v2 = v1[0]
                print(v)
                final_values.append(v2)
            if i == 'lead_owner':
                f=int(l_mobile)
                values = {'name': f }
                v = frappe.db.sql("""select lead_owner from `tabLead` where mobile_no= %(name)s;""", values=values)
                print("This is lead_owner")
                v1 = v[0]
                v2 = v1[0]
                print(v)
                final_values.append(v2)
            if i == 'gender':
                f=int(l_mobile)
                values = {'name': f }
                v = frappe.db.sql("""select gender from `tabLead` where mobile_no= %(name)s;""", values=values)
                print("This is gender")
                v1 = v[0]
                v2 = v1[0]
                print(v)
                final_values.append(v2)
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
def send_messages(l_mobile=0, template='welcome_to_new_customer_default_template_v2', l_name='', is_template=True, message='Hello'):
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
        if is_template:
            url = f"{api_endpoint}/{name_type}/{version}/sendTemplateMessage?whatsappNumber={mobile}"
            bt = bulk_templates(template, l_mobile=mobile)
            print("\n\n bt", bt, "\n\n")
            payload = {
                    "parameters": bt,
                    "broadcast_name": template,
                    "template_name": template
                }
            response = requests.post(url, json=payload, headers=headers)
        else:
            url = f"{api_endpoint}/{name_type}/{version}/sendSessionMessage/whatsappNumber={mobile}?messageText={message}"
            response = requests.post(url, headers=headers)


        print("\n\n response sdfgaf ", response, "\n\n")
    return response


@frappe.whitelist(allow_guest=True)
def send(name='', number='', requesttype='', equipment='', textarea=''):
    print("\n\n okey method called \n\n")
    print("\n\n name", name, "\n\n")
    print("\n\n req ty", requesttype, "\n\n")
    print("\n\n equpment", equipment, "\n\n")
    print("\n\n textarea", textarea, "\n\n")

    template = 'welcome_to_new_customer_default_template_v2'
    template1 = 'shopify_default_ordershipment_tracking_url_v5'
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

    # data = {
    #     "result": "success",
    #     "messages": {
    #         "items": [
    #             {
    #                 "eventDescription": "Broadcast message with using \"welcome_to_new_customer_default_template_v2\" template was received 24|11|2022",
    #                 "finalText": "Hi Rakesh 👋🏻\n\nWelcome to WATI Demo!\n\nClick below button to send your first message 👇🏻",
    #                 "template": None,
    #                 "mediaheaderLink": None,
    #                 "statusstring": "READ",
    #                 "faileddetail": "",
    #                 "localmessageid": None,
    #                 "id": "637f7ee7d97ed08f2d7a24b4",
    #                 "created": "2022-11-24T14:25:43.736Z",
    #                 "conversationid": "637f7e3fd97ed08f2d7a244c",
    #                 "ticketid": None,
    #                 "eventtype": "broadcastMessage"
    #             },
    #             {
    #                 "replysourcemessage": None,
    #                 "messagereferral": None,
    #                 "text": "hii",
    #                 "type": "text",
    #                 "data": None,
    #                 "timestamp": "1669299815",
    #                 "owner": True,
    #                 "statusstring": "READ",
    #                 "avatarurl": None,
    #                 "assignedid": "637de276267008b0938b4415",
    #                 "operatorname": "Nilesh Pithiya",
    #                 "localmessageid": None,
    #                 "faileddetail": "",
    #                 "contacts": None,
    #                 "id": "637f7e68d97ed08f2d7a2463",
    #                 "created": "2022-11-24T14:23:36.141Z",
    #                 "conversationid": "637f7e3fd97ed08f2d7a244c",
    #                 "ticketid": "637f7e56d97ed08f2d7a2454",
    #                 "eventtype": "message"
    #             },
    #             {
    #                 "eventDescription": "Chat is now assigned to nilesh@sanskartechnolab.com. Automation will not work unless it's assigned back to Bot",
    #                 "type": 1,
    #                 "actor": "nilesh@sanskartechnolab.com",
    #                 "assignee": "nilesh@sanskartechnolab.com",
    #                 "topicname": None,
    #                 "id": "637f7e67d97ed08f2d7a245f",
    #                 "created": "2022-11-24T14:23:35.982Z",
    #                 "conversationid": "637f7e3fd97ed08f2d7a244c",
    #                 "ticketid": "637f7e56d97ed08f2d7a2454",
    #                 "eventtype": "ticket"
    #             },
    #             {
    #                 "eventDescription": "The ticket has been assigned to Bot by Bot",
    #                 "type": 1,
    #                 "actor": "Bot",
    #                 "assignee": "Bot",
    #                 "topicname": None,
    #                 "id": "637f7e56d97ed08f2d7a2458",
    #                 "created": "2022-11-24T14:23:18.747Z",
    #                 "conversationid": "637f7e3fd97ed08f2d7a244c",
    #                 "ticketid": "637f7e56d97ed08f2d7a2454",
    #                 "eventtype": "ticket"
    #             },
    #             {
    #                 "replysourcemessage": None,
    #                 "messagereferral": None,
    #                 "text": "Hello",
    #                 "type": "text",
    #                 "data": None,
    #                 "timestamp": "1669299798",
    #                 "owner": False,
    #                 "statusstring": "SENT",
    #                 "avatarurl": None,
    #                 "assignedid": None,
    #                 "operatorname": None,
    #                 "localmessageid": None,
    #                 "faileddetail": None,
    #                 "contacts": None,
    #                 "id": "637f7e56d97ed08f2d7a2457",
    #                 "created": "2022-11-24T14:23:18.305Z",
    #                 "conversationid": "637f7e3fd97ed08f2d7a244c",
    #                 "ticketid": "637f7e56d97ed08f2d7a2454",
    #                 "eventtype": "message"
    #             },
    #             {
    #                 "eventdescription": "The chat has been initialized by contact Rakesh (917016677607)",
    #                 "type": 0,
    #                 "actor": None,
    #                 "assignee": None,
    #                 "topicname": "General Enquiry",
    #                 "id": "637f7e56d97ed08f2d7a2455",
    #                 "created": "2022-11-24T14:23:18.287Z",
    #                 "conversationid": "637f7e3fd97ed08f2d7a244c",
    #                 "ticketid": "637f7e56d97ed08f2d7a2454",
    #                 "eventtype": "ticket"
    #             },
    #             {
    #                 "eventdescription": "Broadcast message with using \"welcome_to_new_customer_default_template_v2\" template was received 24|11|2022",
    #                 "finalText": "Hi Rakesh 👋🏻\n\nWelcome to WATI Demo!\n\nClick below button to send your first message 👇🏻",
    #                 "template": None,
    #                 "mediaheaderLink": None,
    #                 "statusstring": "READ",
    #                 "faileddetail": "",
    #                 "localmessageid": None,
    #                 "id": "637f7e40d97ed08f2d7a244e",
    #                 "created": "2022-11-24T14:22:56.007Z",
    #                 "conversationid": "637f7e3fd97ed08f2d7a244c",
    #                 "ticketid": None,
    #                 "eventtype": "broadcastMessage"
    #             }
    #         ],
    #         "pageNumber": 1,
    #         "pageSize": 100,
    #         "convCount": 0,
    #         "total": 2,
    #         "grandTotal": 0,
    #         "orderBy": None,
    #         "lastId": None,
    #         "sortBy": 0,
    #         "filters": None,
    #         "allowFilters": None,
    #         "search": None
    #     },
    #     "link": {
    #         "prevPage": None,
    #         "nextPage": None,
    #         "pageNumber": 1,
    #         "pageSize": 100,
    #         "total": 2
    #     }
    # }
    # data = data['messages']['items']
    #
    # # data = [{
    # # "first_name": "Nilesh",
    # # "last_name": "Pithiya",
    # # "phone": "+917990915950"
    # # },
    # #     {
    # #         "first_name": "Mahesh",
    # #         "last_name": "Pithiya",
    # #         "phone": "+917990915950"
    # #     },
    # #     {
    # #         "first_name": "Suresh",
    # #         "last_name": "Pithiya",
    # #         "phone": "+917990915950"
    # #     }
    # # ]
    #
    # for i in data:
    #     print("\n\n", i, "\n\n")
    #     access_token = 'Token 751776116cb5857:320715c4c0282b1'
    #     headers = {"Content-Type": "text/json", "Authorization": access_token}
    #     url = "http://adani.com:8019/api/resource/Whatsapp Chat"
    #     payload = i
    #     print("\n\n payload", payload, "\n\n")
    #     response = requests.post(url, json=payload, headers=headers)
    #     print("\n\n", response, "\n\n")
    #
    #
    # # print("\n\n data", data, "\n\n")
    # # print("\n\n statusstring", data[0]['statusstring'], "\n\n")
    # # print("\n\n data", data['messages']['items'], "\n\n")


# ************************************* below code for load data ***********************************************************

    # name = frappe.db.get_list("Lead", filters={"phone": mobile}, fields=["name"])
    # chat = frappe.db.get_value("wati call message log", filters={'phone': mobile}, fieldname=["data"])
    #
    # data = json.loads(chat)
    # ok = {"name": "nilesh", "phone": "917990915950", "owner": "true", "message": "hello"}
    # demo = data['data']
    # demo.append(ok)
    # print("\n\n deta1 ", type(demo), "\n\n")
    # print("\n\n deta1 ", demo, "\n\n")


# ****************************************************************************

    wa_data = {"id": "message.Id", "waId": "918690396934", }

    se_mo = wa_data["waId"]
    f_data, name = frappe.db.get_value("wati call message log", filters={"phone": f"{se_mo}"}, fieldname=["data", "name"])

    if f_data is not None:
        data = json.loads(f_data)
        data['data'].append(data)
        # frappe.db.set_value('wati call message log', f'{name}', 'data', f'{data}')
    else:
        data = {"data": []}
        data['data'].append(wa_data)
        data = json.dumps(data)
        print("\n\n type", type(data))
        frappe.db.sql(f'update `tabwati call message log` set data = {data} where name="{name}"')
        # frappe.db.set_value('wati call message log', f'{name}', 'data', f'{data}')
