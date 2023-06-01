frappe.listview_settings['Templates'] = {
    onload: function(listview) {
        listview.page.add_inner_button('Get Templates', function() {
               frappe.call({
                method: 'whatsapp_app.whatsapp_app.doctype.api.get_template',
                callback: function(response) {
                    console.log(response.text);
                }
            });
        });
    }
};
