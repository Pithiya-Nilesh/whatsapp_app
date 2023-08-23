frappe.listview_settings['Lead'].onload = function(listview) {
  const currentUserRoles = frappe.user_roles;
  const hasWhatsAppManagerRole = currentUserRoles.includes('WhatsApp Manager');
  const isAdmin = currentUserRoles.includes('Administrator');

  if (hasWhatsAppManagerRole || isAdmin) {
    listview.page.add_action_item(__("Send Whatsapp Template"), function() {
      test(listview);
    });
  }
};

function test(listview) {
  let names = [];
  $.each(listview.get_checked_items(), function(key, value) {
    names.push(value.name);
  });
  if (names.length === 0) {
    frappe.throw(__("No rows selected."));
  }

  frappe.call({
    method: 'whatsapp_app.whatsapp_app.doctype.api.get_template_list',
    args: {
      'doctype': doctype
    },
    callback: (r) => {
      if (r.message) {
        const template = r.message;

        frappe.call({
          method: 'frappe.client.get_list',
          args: {
            'doctype': 'Templates',
            'filters': {
              'name': ['in', template]
            },
            'fields': ['name', 'status','sample'],
            'limit_start': 0,  
            'limit_page_length': 0  
          },

          callback: function(response) {
            if (response.message) {
              const templateData = response.message;
              const customerDoctype = doctype;
              const customerFields = frappe.get_meta(customerDoctype).fields.filter(field => {
                return field.fieldtype !== 'Column Break' && field.fieldtype !== 'Section Break';
              }).map(field => {
                return {
                  fieldname: field.fieldname,
                  label: field.label
                };
              });

              const customerFieldLabels = customerFields.map(fieldname => {
                const fieldMeta = frappe.get_meta(doctype).fields.find(field => field.fieldname === fieldname);
                return fieldMeta ? fieldMeta.label : fieldname;
              });


              const d1 = new frappe.ui.Dialog({
                title: 'Send Message',
                fields: [
                  {
                    label: 'Select Template',
                    fieldname: 'select_template',
                    fieldtype: 'Select',
                    options: template,
                    onchange: function() {
                      const selectedValue = this.get_value();
                      const previousValue = this.last_value;
                      if (selectedValue && selectedValue !== previousValue) {
                        this.last_value = selectedValue;
                        const selectedTemplateData = templateData.find((template) => template.name === selectedValue);
                        if (selectedTemplateData) {
                          const dynamicVariables = extractDynamicVariables(selectedTemplateData.sample);

                          const variableData = dynamicVariables.map(variable => ({
                            variable_name: variable,
                            variable_value: '',
                            is_dynamic: 0,
                            doctype_field: ''
                          }));
                          renderTable(variableData);
                          } else {
                            renderTable([]);
                          }
                      }
                    }
                  }
                ],
                primary_action_label: 'Send',

                primary_action(values) {
                  const selectTemplateValue = d1.get_value('select_template');

                  if (!selectTemplateValue) {
                    frappe.msgprint('Please select a template.');
                    return;
                  }
                    
                  const tableData = getTableData();
                  const dataList = tableData.map(row => ({
                    name: row.variable_name,
                    is_dynamic: row.is_dynamic ? 1 : 0,
                    value: row.is_dynamic ? row.doctype_field : row.variable_value
                  }));
                  
                  if (dataList.length === 0) {
                        frappe.msgprint('Nothing to send whatsapp message here!');
                        return;
                     }

                  const hasEmptyValue = dataList.some(row => !row.value);
                  if (hasEmptyValue) {
                    frappe.msgprint('Please fill in the Variable Value fields.');
                    return;
                  }

                  showConfirmDialog(listview);

                  d1.hide();
                }
              });
 
              const tableSection = $('<div>').appendTo(d1.body);

              function renderTable(data) {
                tableSection.empty();
                if (data.length === 0) {
                    const noDataMessage = $('<p>').text('No dynamic variable is available in this template').appendTo(tableSection);
                    return;
                }


                const table = $('<table class="table table-bordered" id="tabledata">').appendTo(tableSection);
                const thead = $('<thead>').appendTo(table);
                const tbody = $('<tbody>').appendTo(table);

                const headerRow = $('<tr>').appendTo(thead);
                $('<th>').text('Variable Name').appendTo(headerRow);
                $('<th>').text('Is Dynamic').appendTo(headerRow);
                $('<th>').text('Variable Value').appendTo(headerRow);

                data.forEach(row => {
                  const variableName = row.variable_name;
                  const variableValue = row.variable_value;
                  const isDynamic = row.is_dynamic;
                  const doctypeField = row.doctype_field;

                  const rowElement = $('<tr>').appendTo(tbody);
                  $('<td>').text(variableName).appendTo(rowElement);
                  const dynamicCheckbox = $('<input type="checkbox">').prop('checked', !!isDynamic).appendTo($('<td>').appendTo(rowElement));
                  const variableValueInput = $('<td>').appendTo(rowElement);
                  if (isDynamic) {
                    const selectField = $('<select>').css({ width: '200px', height: '30px' }).appendTo(variableValueInput);

                    customerFields.forEach(field => {
                      $('<option>').text(field.label).val(field.fieldname).appendTo(selectField);
                    });

                    selectField.val(doctypeField);
                  } else {
                      $('<input type="text">')
                        .val(variableValue)
                        .css({ width: '200px', height: '30px' })  // Set the desired width and height
                        .appendTo(variableValueInput);
                    }

                  dynamicCheckbox.on('change', function() {
                    const isChecked = $(this).is(':checked');
                    row.is_dynamic = isChecked ? 1 : 0;
                    if (isChecked) {
                      variableValueInput.empty();
                      const selectField = $('<select>').css({ width: '200px', height: '30px' }).appendTo(variableValueInput);

                      customerFields.forEach(field => {
                        $('<option>').text(field.label).val(field.fieldname).appendTo(selectField);
                      });

                      selectField.val(doctypeField);
                      row.doctype_field = doctypeField; // Store the selected fieldname
                    } else {
                      variableValueInput.empty();
                      $('<input type="text">').val(row.variable_value).css({ width: '200px', height: '30px' }).appendTo(variableValueInput);
                      row.doctype_field = ''; // Clear the stored fieldname
                    }
                  });

                  variableValueInput.on('change', function() {
                    const selectedValue = $(this).val();
                    if (isDynamic) {
                      row.doctype_field = selectedValue;
                    } else {
                      row.variable_value = selectedValue;
                    }
                  });
                });
              }

          function showConfirmDialog(listview) {
  const selectedCustomerNames = listview.get_checked_items().map(item => item.title); // Use item.title instead of item.name
  const selectTemplateValue = d1.get_value('select_template');
  const selectedTemplateData = templateData.find(template => template.name === selectTemplateValue);
  const templateSample = selectedTemplateData ? selectedTemplateData.sample : '';
  const tableData = getTableData();
  const dataList = tableData.map(row => ({
    name: row.variable_name,
    is_dynamic: row.is_dynamic ? 1 : 0,
    value: row.is_dynamic ? row.doctype_field : row.variable_value
  }));
  console.log(selectedCustomerNames);

  const updatedTemplateSample = selectedTemplateData.sample.replace(/{{([^{}]+)}}/g, (match, variable) => {
    const variableRow = dataList.find(row => row.name === variable);
    if (variableRow && variableRow.is_dynamic) {
      return `{{ ${variableRow.value} }}`;
    } else if (variableRow) {
      return variableRow.value;
    } else {
      return match;
    }
  });

  frappe.call({
    method: 'frappe.client.get_list',
    args: {
      doctype: 'Lead',
      filters: { title: ['in', selectedCustomerNames] }, // Use 'title' instead of 'name' in the filters
      fields: ['name', 'whatsapp_no','title'], // Include 'whatsapp_no' field
      limit_start: 0,
      limit_page_length: 0
    },
    callback: function(response) {
      if (response.message) {
        const selectedCustomers = response.message;
        const whatsappNos = selectedCustomers.map(customer => customer.whatsapp_no);

        const confirmDialog = new frappe.ui.Dialog({
          title: 'Whatsapp Message',
          fields: [
            {
              fieldtype: 'HTML',
              options: `
                <div class="template-preview">
                  <h5>Template Sample</h5>
                  <div class="sample-data">${updatedTemplateSample.replace(/\n/g, '<br>')}</div>
                </div>
                <table class="table table-bordered">
                  <thead>
                    <tr>
                      <th><input type="checkbox" id="select-all-checkbox" style="vertical-align: middle;"></th>
                      <th style="display: none;">Names</th>
                      <th>Title</th>
                      <th>Whatsapp Number</th>
                      <th></th>
                    </tr>
                  </thead>
                  <tbody>
                    ${selectedCustomers
                      .map(
                        (customer, index) => `
                      <tr>
                        <td><input type="checkbox" class="row-checkbox" style="vertical-align: middle;" ${
                          whatsappNos[index] ? 'checked' : ''
                        } ${whatsappNos[index] ? '' : 'disabled'}></td>
                        <td style="display: none;">${customer.name}</td>
                        <td>${customer.title}</td>
                        <td>${whatsappNos[index] ? whatsappNos[index] : 'Whatsapp number not found'}</td>
                        <td class="text-center"><button class="btn btn-default delete-row-btn" data-index="${index}" style="background-color: #f4f5f6; color: #808080;"><i class="fa fa-trash" style="font-size: 16px;"></i></button></td>
                      </tr>
                    `
                      )
                      .join('')}
                  </tbody>
                </table>
              `,
            },
          ],
          primary_action_label: 'Confirm',
          primary_action() {
            const selectedCustomerName = Array.from(confirmDialog.body.querySelectorAll('input.row-checkbox:checked')).map(
              checkbox => {
                const row = checkbox.closest('tr');
                return row.querySelector('td:nth-child(2)').textContent.trim();
              }
            );

            if (selectedCustomerName.length === 0) {
              frappe.msgprint('Please select a lead to send the WhatsApp message.');
              return;
            }

            const sendConfirmationDialog = new frappe.ui.Dialog({
              title: 'Confirmation',
              fields: [
                {
                  fieldtype: 'HTML',
                  options: `<div>Do you want to send the WhatsApp message?</div>`,
                },
              ],
              primary_action_label: 'Yes',
              secondary_action_label: 'No',
              primary_action() {
                const selectedCustomerNames = Array.from(confirmDialog.body.querySelectorAll('input.row-checkbox:checked')).map(
                  checkbox => {
                    const row = checkbox.closest('tr');
                    return row.querySelector('td:nth-child(2)').textContent.trim();
                  }
                );

                const tableData = getTableData();
                const dataList = tableData.map(row => ({
                  name: row.variable_name,
                  is_dynamic: row.is_dynamic ? 1 : 0,
                  value: row.is_dynamic ? row.doctype_field : row.variable_value
                }));

                frappe.call({
                  method: 'whatsapp_app.whatsapp_app.doctype.api.send_bulk_whatsapp_message',
                  args: {
                    template_name: selectTemplateValue,
                    doctype: 'Lead',
                    name: selectedCustomerNames, 
                    data: dataList,
                  },
                  freeze: true,
                  callback: r => {
                    frappe.msgprint('Message sent');
                  },
                  error: r => {
                    frappe.msgprint('Something went wrong!');
                  }
                });

                sendConfirmationDialog.hide();
                confirmDialog.hide();
              },
              secondary_action() {
                sendConfirmationDialog.hide();
              },
            });

            sendConfirmationDialog.show();
          },
        });

        confirmDialog.body.querySelectorAll('.delete-row-btn').forEach(button => {
          button.addEventListener('click', function() {
            const row = this.closest('tr');
            const index = parseInt(this.dataset.index);
            row.remove();
          });
        });

        const checkboxes = confirmDialog.body.querySelectorAll('.row-checkbox:not([disabled])');
        const selectAllCheckbox = confirmDialog.body.querySelector('#select-all-checkbox');

        selectAllCheckbox.addEventListener('change', function() {
          checkboxes.forEach(checkbox => {
            if (!checkbox.disabled) {
              checkbox.checked = this.checked;
            }
          });
        });

        checkboxes.forEach(checkbox => {
          checkbox.addEventListener('change', function() {
            const allChecked = Array.from(checkboxes).every(checkbox => checkbox.checked);
            selectAllCheckbox.checked = allChecked;
          });
        });

        confirmDialog.body.querySelectorAll('.eye-icon-btn').forEach(button => {
          button.addEventListener('click', function() {
            const customerDetailsDialog = new frappe.ui.Dialog({
              title: 'Whatsapp Message Preview',
              fields: [
                {
                  fieldtype: 'HTML',
                  options: `
                    <div class="sample-data">${updatedTemplateSample.replace(/\n/g, '<br>')}</div>
                  `,
                },
              ],
              primary_action_label: 'OK',
              primary_action() {
                customerDetailsDialog.hide();
              },
            });

            customerDetailsDialog.show();
          });
        });

        confirmDialog.show();
      }
    },
  });
}

              function getTableData() {
                const table = tableSection.find('#tabledata');
                const data = [];

                table.find('tbody tr').each((index, element) => {
                  const variableName = $(element).find('td:nth-child(1)').text();
                  const isDynamic = $(element).find('input[type="checkbox"]').is(':checked');
                  const doctypeField = $(element).find('select').val();
                  const variableValueInput = $(element).find('input[type="text"]');
                  const variableValue = isDynamic ? doctypeField : variableValueInput.val();

                  data.push({
                    variable_name: variableName,
                    variable_value: variableValue,
                    is_dynamic: isDynamic ? 1 : 0,
                    doctype_field: doctypeField
                  });
                });

                return data;
              }


              d1.show();
            }
          },
          error: (r) => {
            frappe.msgprint('something went wrong!');
          }
        });
      }
    },
    error: (r) => {
      frappe.msgprint('something went wrong!');
    }
  });
}

function extractDynamicVariables(templateSample) {
  const regex = /{{([^{}]+)}}/g; 
  const matches = [];
  let match;

  while ((match = regex.exec(templateSample)) !== null) {
    matches.push(match[1]);
  }

  return matches;
}
