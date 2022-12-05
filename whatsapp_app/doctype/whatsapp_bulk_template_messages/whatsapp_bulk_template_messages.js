// Copyright (c) 2022, Srushti Shah And Foram Shah and contributors
// For license information, please see license.txt

frappe.ui.form.on('WhatsApp Bulk Template Messages', {
	refresh: function(frm) {
		frm.add_custom_button(('Send Template Message'),
        function()
        {
			// let l_mobile= frm.doc.hidden_list
			let l_mobile= frm.doc.receiver_list
			console.log("mobile number", l_mobile)
            // console.log(l_mobile.length)
			// console.log(l_mobile)
			let template = frm.doc.select_template
			// console.log(d_template)
			frappe.call({
				method: "whatsapp_app.whatsapp_app.doctype.api.send_messages",
				args: {'l_mobile':l_mobile, 'template':template},
				callback: function(r)
				{
//					frappe.throw(r.message)
                    console.log(r.message)
				}
			});
            // frappe.show_alert(__(`Template message sent ${ l_Name }`));
        },("Whatsapp Send Message"))
	}
});
