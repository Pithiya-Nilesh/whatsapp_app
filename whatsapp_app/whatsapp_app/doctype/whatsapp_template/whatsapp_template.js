// Copyright (c) 2022, Srushti Shah And Foram Shah and contributors
// For license information, please see license.txt

frappe.ui.form.on('Whatsapp Template', {
	refresh: function(frm) {
		frm.add_custom_button(('Send Template Message'),
        function()
        {
			let l_name= frm.doc.lead_name
            // console.log(l_Name)
			let template = frm.doc.template
			// console.log(d_template)
			frappe.call({
				method: "whatsapp_app.whatsapp_app.doctype.api.send_messages",
				args: {'l_name':l_name, 'template':template},
				callback: function(r)
				{
//				    frappe.throw(r.message)
                    console.log(r.message)
				}
			});
            frappe.show_alert(__(`Template message sent ${ l_name }`));
        },("Whatsapp Send Message"))
	}
});
