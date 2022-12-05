import json

import frappe


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
    se_mo = wa_data["waId"]
    f_data, name = frappe.db.get_value("wati call message log", filters={"phone": f"{se_mo}"},
                                       fieldname=["data", "name"])
    if f_data is not None:
        raw_data = json.loads(f_data)
        raw_data['data'].append(wa_data)
        data = json.dumps(raw_data)
        frappe.db.set_value('wati call message log', f'{name}', 'data', f'{data}')
    else:
        data = {"data": []}
        data['data'].append(wa_data)
        data = json.dumps(data)
        frappe.db.set_value('wati call message log', f'{name}', 'data', f'{data}')
    return 'success'

@frappe.whitelist(allow_guest=True)
def wati_webhooks():

    data1 = frappe.call(data, **frappe.form_dict)
    # data1 = frappe.local.form_dict
    # user = frappe.get_doc(doctype='wati call message log', first_name='asdfleshdsfgsfd')
    # user.insert()
    return data1


# def send_report_on_whatsapp():
#     data = frappe.get_doc("wati call message log")
#     data.first_name = "nilesh"
#     data.insert()
#     frappe.db.commit()
#     print("\n\n okey its run")
