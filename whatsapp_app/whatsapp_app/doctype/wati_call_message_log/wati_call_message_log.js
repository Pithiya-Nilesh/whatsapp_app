// Copyright (c) 2022, Srushti Shah And Foram Shah and contributors
// For license information, please see license.txt

frappe.ui.form.on('wati call message log', {
	onload: function(frm) {
        frm.set_value({
            read: 1,
        })
        frm.save();
	 }
});
