// Copyright (c) 2022, Srushti Shah And Foram Shah and contributors
// For license information, please see license.txt

frappe.ui.form.on('Whatsapp Campaign', {
	whatsapp_campaign_for: function(frm) {
		frm.set_value('recipient', '');
	}
});
