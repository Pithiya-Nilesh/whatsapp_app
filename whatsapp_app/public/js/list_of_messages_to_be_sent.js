frappe.ui.form.on("List of WhatsApp Messages to be Sent", {
    refresh: function (frm) {
  
        // var currentUserRoles = frappe.user_roles;
        // var isAdmin = currentUserRoles.includes("Administrator");

        // const hasWhatsAppManagerRole = currentUserRoles.includes('WhatsApp Manager');

        // if (hasWhatsAppManagerRole || isAdmin) {
            if(frm.doc.sent == 0){
                frm.add_custom_button(__("Send Whatsapp Message"), function(){
                    frappe.show_progress(__('Sending messages'), 5);
                    frappe.call({
                        method: 'whatsapp_app.whatsapp_app.doctype.api.send_messages_from_list_of_reminder',
                        args: {
                            name: frm.doc.name
                        },
                        callback: function(r) {
                            console.log("asdf", r)
                            frappe.hide_progress();
                            // if (!r.exc) {
                                
                            // }
                        }
                    })
                });
            }
              
        // }


    }
})