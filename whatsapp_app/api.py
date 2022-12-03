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


@frappe.whitelist(allow_guest=True)
def wati_webhooks(id):

    print("\n\n id", id, "\n\n")
    # data = frappe.db.get_value("wati call message log", "8015f16194", "data")
    # data = frappe.parse_json(data)

    # print("\n\n its working", json, "\n\n")
    # print("\n\n type", type(json), "\n\n")
    #print("\n\n post kwargs")


def send_report_on_whatsapp():
    # data = frappe.get_doc("wati call message log")
    # data.first_name = "nilesh"
    # data.insert()
    # frappe.db.commit()
    print("\n\n okey its run")