    
frappe.ui.form.on("Raw Data", {
    refresh(frm) {
        var f_name = cur_frm.doc.full_name;

        var container = $('<div class="custom-container">').appendTo(frm.wrapper);

        container.css({
            width: "30%",
            height: "65%",
            backgroundColor: "#ece5dd",
            position: "fixed",
            top: "50%",
            right: "80px",
            transform: "translateY(-50%)",
            borderRadius: "5px",
            boxShadow: "0 0 5px rgba(0, 0, 0, 0.4)",
            zIndex: 9999,
            display: "none",
        });

        var headingDiv = $("<div>")
            .css("background-color", "#128c7e")
            .appendTo(container);

        var closeButtonElement = $("<button>")
            .css("float", "right")
            .appendTo(headingDiv);

        var closeIconElement = $("<i>")
            .addClass("fa fa-close")
            .css("font-size", "30px");

        closeButtonElement.prepend(closeIconElement);

        closeButtonElement.css({
            float: "right",
            backgroundColor: "#128c7e",
            marginRight: "10px",
            marginTop: "10px",
            color: "#FFF",
            border: "none",
            borderRadius: "4px",
            fontWeight: "bold",
            cursor: "pointer",
        });

        var heading = $("<h3>")
            .css("padding-left", "10px")
            .css("color", "white")
            .css("margin-bottom", "0px")
            .css("background-color", "#128c7e")
            .css("padding-top", "15px")
            .css("padding-bottom", "15px")
            .text(f_name)
            .appendTo(headingDiv);

        var messagesDiv = $("<div>")
            .css("overflow-y", "scroll")
            .css("background-color", "#ece5dd")
            .css("height", "83%")
            .appendTo(container);
        
        var statusElement;
        var expiredMessageAdded = false;
        
        var allElement = $("<div>")
            .css("height", "40px")
            .css("padding-top", "5px")
            .css("background-color", "#ece5dd")
            .css("display", "flex")
            .css("flex-direction", "row")
            .appendTo(container);


        var buttonElement1 = $("<button>").text("Template");

        buttonElement1.css({
            height: "25px",
            backgroundColor: "#128c7e",
            marginLeft: "5px",
            marginTop: "4px",
            color: "#FFF",
            padding: "2px 4px",
            border: "none",
            borderRadius: "4px",
            fontWeight: "bold",
            cursor: "pointer",
        });

        var inputElement = $("<input>")
            .attr("type", "text")
            .attr("placeholder", " Type a message...");

        inputElement.css({
            marginLeft: "5px",
            marginRight: "5px",
            border: "none",
            marginTop: "5px",
            height: "25px",
            borderRadius: "4px",
            width: "auto",
            flex: "1"
        });

        var buttonElement = $("<button>");

        var iconElement = $("<i>")
            .addClass("fa fa-paper-plane");

        buttonElement.prepend(iconElement);

        buttonElement.css({
            height: "30px",
            backgroundColor: "#128c7e",
            marginTop: "2px",
            marginRight: "10px",
            color: "#FFF",
            padding: "4px 8px",
            border: "none",
            borderRadius: "4px",
            fontWeight: "bold",
            cursor: "pointer",
        });


        var showButtonClicked = true;

        var currentUserRoles = frappe.user_roles;
        var isAdmin = currentUserRoles.includes("Administrator");

        const hasWhatsAppManagerRole = currentUserRoles.includes('WhatsApp Manager');

        if (hasWhatsAppManagerRole || isAdmin) {
            if (frm.doc.whatsapp_no) {
                frm.add_custom_button(
                    '<i class="fa fa-whatsapp" aria-hidden="true" style="font-size:24px;color:#25d366" ></i>',
                    function () {
                        // var doctype = cur_frm.doctype;
                        var phone = cur_frm.doc.whatsapp_no;
                        var availableLog;
                        frappe.call({
                            method: "frappe.client.get_list",
                            args: {
                                doctype: "wati call message log",
                                filters: {
                                    name: phone,
                                },
                                fields: ["name"]
                            },
                            callback: function (response) {

                                var message = response.message;
                                var doctype = cur_frm.doctype;
                                if (message && message.length > 0) {
                                    var ans = message[0];
                                    var ans_name = ans.name;


                                    frappe.call({
                                        method:
                                            "whatsapp_app.whatsapp_app.doctype.api.get_template_sample",
                                        args: {
                                            phone: phone,
                                        },
                                        async: false,
                                        callback: function (response) { },
                                    });
                                    frappe.call({
                                        method: "whatsapp_app.whatsapp_app.doctype.api.get_img",
                                        args: {
                                            phone: phone,
                                        },
                                        async: false,
                                        callback: function (response) { },
                                    });
                                    frappe.call({
                                        method: "frappe.client.get_list",
                                        args: {
                                            doctype: "wati call message log",
                                            filters: {
                                                name: phone,
                                            },
                                            fields: ["name", "data"],
                                        },
                                        callback: function (response) {
                                            if (response.message) {
                                                var dataObj = response.message;
                                                if (dataObj && dataObj.length > 0) {
                                                    var dataValue = dataObj[0].data;

                                                    var parsedData = JSON.parse(dataValue);
                                                    var result = parsedData.data;

                                                    var desiredDictionaries = [];
                                                    var tempName;
                                                    var tempImg;

                                                    for (var i = 0; i < result.length; i++) {
                                                        var dictionary = result[i];

                                                        if (
                                                            dictionary.message &&
                                                            dictionary.message.hasOwnProperty("isOwner")
                                                        ) {
                                                            desiredDictionaries.push(dictionary.message);
                                                        } else if (
                                                            dictionary.hasOwnProperty("owner") &&
                                                            !dictionary.owner
                                                        ) {
                                                            desiredDictionaries.push(dictionary);
                                                        } else if (
                                                            dictionary.hasOwnProperty("modified_sample")
                                                        ) {
                                                            tempName = dictionary.modified_sample;

                                                            var timedate = dictionary.send_time;
                                                            tempImg = dictionary.templateImg;

                                                            frappe.call({
                                                                method:
                                                                    "whatsapp_app.whatsapp_app.doctype.api.get_image",
                                                                args: {
                                                                    filename: tempImg,
                                                                },
                                                                async: false,
                                                                callback: function (response) { },
                                                            });

                                                            desiredDictionaries.push({
                                                                tempName: tempName,
                                                                timedate: timedate,
                                                                tempImg: tempImg,
                                                            });
                                                        }
                                                    }

                                                    var texts = desiredDictionaries.map(function (
                                                        dictionary
                                                    ) {
                                                        if (
                                                            typeof dictionary === "object" &&
                                                            dictionary.hasOwnProperty("text")
                                                        ) {
                                                            var text = dictionary.text;
                                                        } else if (
                                                            typeof dictionary === "object" &&
                                                            dictionary.hasOwnProperty("tempName") &&
                                                            dictionary.hasOwnProperty("timedate") &&
                                                            dictionary.hasOwnProperty("tempImg")
                                                        ) {
                                                        } else {
                                                            return dictionary;
                                                        }
                                                    });

                                                    container.empty();
                                                    headingDiv.appendTo(container);
                                                    messagesDiv.appendTo(container);

                                                    messagesDiv.empty();

                                                    allElement.appendTo(container);

                                                    for (var j = 0; j < texts.length; j++) {
                                                        var text = texts[j];
                                                        var created = "";

                                                        if (desiredDictionaries[j].hasOwnProperty("text")) {
                                                            text = desiredDictionaries[j].text;
                                                            if (
                                                                desiredDictionaries[j].hasOwnProperty("created")
                                                            ) {
                                                                var datetimeString = desiredDictionaries[j].created;
                                                                var dateObj = new Date(datetimeString);

                                                                var day = dateObj.getUTCDate();
                                                                var month = dateObj.getUTCMonth() + 1;
                                                                var year = dateObj.getUTCFullYear();

                                                                var hours = dateObj.getUTCHours();
                                                                var minutes = dateObj.getUTCMinutes();
                                                                var seconds = dateObj.getUTCSeconds();

                                                                if (day < 10) {
                                                                    day = "0" + day;
                                                                }
                                                                if (month < 10) {
                                                                    month = "0" + month;
                                                                }
                                                                if (hours < 10) {
                                                                    hours = "0" + hours;
                                                                }
                                                                if (minutes < 10) {
                                                                    minutes = "0" + minutes;
                                                                }
                                                                if (seconds < 10) {
                                                                    seconds = "0" + seconds;
                                                                }

                                                                created =
                                                                    day +
                                                                    "-" +
                                                                    month +
                                                                    "-" +
                                                                    year +
                                                                    " " +
                                                                    hours +
                                                                    ":" +
                                                                    minutes +
                                                                    ":" +
                                                                    seconds;
                                                            }
                                                        }

                                                        var textElement = $("<p>")
                                                            .css(
                                                                "padding-right",
                                                                desiredDictionaries[j].owner === false
                                                                    ? "100px"
                                                                    : "10px"
                                                            )
                                                            .css(
                                                                "padding-left",
                                                                desiredDictionaries[j].owner === false
                                                                    ? "10px"
                                                                    : "100px"
                                                            )
                                                            .css(
                                                                "text-align",
                                                                desiredDictionaries[j].owner === false
                                                                    ? "left"
                                                                    : "right"
                                                            )
                                                            .appendTo(messagesDiv);

                                                        var textContent = $("<div>")
                                                            .css(
                                                                "background-color",
                                                                desiredDictionaries[j].owner === false
                                                                    ? "#fff"
                                                                    : "#dcf8c6"
                                                            )
                                                            .css("padding", "10px")
                                                            .css("padding-bottom", "20px")
                                                            .css("border-radius", "10px")
                                                            .text(text)
                                                            .appendTo(textElement);

                                                        if (desiredDictionaries[j].tempImg) {
                                                            var tempImgElement = $("<img>")
                                                                .attr(
                                                                    "src",
                                                                    "https://migoostage.frappe.cloud/files/" +
                                                                    desiredDictionaries[j].tempImg
                                                                )
                                                                .appendTo(textContent);
                                                        }

                                                        var tempNameElement = $("<p>")
                                                            .text(desiredDictionaries[j].tempName)
                                                            .appendTo(textContent);

                                                        var timedateElement = $("<p>")
                                                            .text(desiredDictionaries[j].timedate)
                                                            .css("color", "#808080")
                                                            .css("font-size", "12px")
                                                            .appendTo(textContent);

                                                        if (created !== "") {
                                                            var createdElement = $("<div>")
                                                                .text(created)
                                                                .css("color", "#808080")
                                                                .css("font-size", "12px")
                                                                .appendTo(textContent);
                                                        }

                                                        var imageSrc = "/files/icons8-done-30.png";

                                                        if (desiredDictionaries[j].owner !== false) {
                                                            var imageElement = $("<img>")
                                                                .attr("src", imageSrc)
                                                                .css("width", "20px")
                                                                .css("float", "right")
                                                                .attr("class", "img1")
                                                                .appendTo(textContent);
                                                        }

                                                        var b_tick;
                                                        frappe.call({
                                                            method: "frappe.client.get_list",
                                                            args: {
                                                                doctype: "wati call message log",
                                                                filters: {
                                                                    name: phone,
                                                                    client_read: 1,
                                                                },
                                                                fields: ["name"],
                                                            },
                                                            callback: function (response) {
                                                                b_tick = response.message[0].name;

                                                                if (b_tick) {
                                                                    imageSrc = "/files/icons8-double-tick-50.png";
                                                                    $(".img1").attr("src", imageSrc);
                                                                }
                                                            },
                                                        });
                                                    }

                                                    setTimeout(function () {
                                                        messagesDiv.scrollTop(messagesDiv[0].scrollHeight);
                                                    }, 0);
                                                }

                                                closeButtonElement.on("click", function () {
                                                    container.hide();
                                                });

                                                if (showButtonClicked) {
                                                    container.show();
                                                    showButtonClicked = true;
                                                }
                                            }

                                            frappe.call({
                                                method:
                                                    "whatsapp_app.whatsapp_app.doctype.api.check_status",
                                                args: {
                                                    number: phone,
                                                },
                                                callback: function (response) {
                                                    if (response.message === "yes") {
                                                        buttonElement1.appendTo(allElement);
                                                        inputElement.appendTo(allElement);
                                                        buttonElement.appendTo(allElement);
                                                    } else {
                                                        if (!expiredMessageAdded) {
                                                            statusElement = $("<p>")
                                                                .css("color", "black")
                                                                .css("margin-top", "5px")
                                                                .css("width", "100%")
                                                                .css("text-align", "center")
                                                                .text("The chat has been expired")
                                                                .appendTo(allElement);
                                        
                                                            expiredMessageAdded = true; 
                                                        }
                                                        buttonElement1.prependTo(allElement);
                                                        buttonElement.appendTo(allElement);
                                                    }
                                                },
                                            });

                                            buttonElement1.click(function () {
                                                var names = cur_frm.doc.name;
                                                frappe.call({
                                                    method:
                                                        "whatsapp_app.whatsapp_app.doctype.api.get_template_list",
                                                    args: {
                                                        doctype: doctype,
                                                    },
                                                    callback: (r) => {
                                                        if (r.message) {
                                                            const template = r.message;

                                                            frappe.call({
                                                                method: "frappe.client.get_list",
                                                                args: {
                                                                    doctype: "Templates",
                                                                    filters: {
                                                                        name: ["in", template],
                                                                    },
                                                                    fields: ["name", "status", "sample"],
                                                                    limit_start: 0,
                                                                    limit_page_length: 0,
                                                                },

                                                                callback: function (response) {
                                                                    if (response.message) {
                                                                        const templateData = response.message;
                                                                        const customerDoctype = doctype;
                                                                        const customerFields = frappe
                                                                            .get_meta(customerDoctype)
                                                                            .fields.filter((field) => {
                                                                                return (
                                                                                    field.fieldtype !== "Column Break" &&
                                                                                    field.fieldtype !== "Section Break"
                                                                                );
                                                                            })
                                                                            .map((field) => {
                                                                                return {
                                                                                    fieldname: field.fieldname,
                                                                                    label: field.label,
                                                                                };
                                                                            });

                                                                        const customerFieldLabels = customerFields.map(
                                                                            (fieldname) => {
                                                                                const fieldMeta = frappe
                                                                                    .get_meta(doctype)
                                                                                    .fields.find(
                                                                                        (field) => field.fieldname === fieldname
                                                                                    );
                                                                                return fieldMeta
                                                                                    ? fieldMeta.label
                                                                                    : fieldname;
                                                                            }
                                                                        );

                                                                        const d1 = new frappe.ui.Dialog({
                                                                            title: "Send Message",
                                                                            fields: [
                                                                                {
                                                                                    label: "Select Template",
                                                                                    fieldname: "select_template",
                                                                                    fieldtype: "Select",
                                                                                    options: template,
                                                                                    onchange: function () {
                                                                                        const selectedValue = this.get_value();
                                                                                        const previousValue = this.last_value;
                                                                                        if (
                                                                                            selectedValue &&
                                                                                            selectedValue !== previousValue
                                                                                        ) {
                                                                                            this.last_value = selectedValue;
                                                                                            const selectedTemplateData =
                                                                                                templateData.find(
                                                                                                    (template) =>
                                                                                                        template.name === selectedValue
                                                                                                );
                                                                                            if (selectedTemplateData) {
                                                                                                const dynamicVariables =
                                                                                                    extractDynamicVariables(
                                                                                                        selectedTemplateData.sample
                                                                                                    );

                                                                                                const variableData =
                                                                                                    dynamicVariables.map(
                                                                                                        (variable) => ({
                                                                                                            variable_name: variable,
                                                                                                            variable_value: "",
                                                                                                            is_dynamic: 0,
                                                                                                            doctype_field: "",
                                                                                                        })
                                                                                                    );

                                                                                                renderTable(variableData);
                                                                                            }
                                                                                        }
                                                                                    },
                                                                                },
                                                                            ],
                                                                            primary_action_label: "Send",

                                                                            primary_action(values) {
                                                                                const tableData = getTableData();
                                                                                const dataList = tableData.map((row) => ({
                                                                                    name: row.variable_name,
                                                                                    is_dynamic: row.is_dynamic ? 1 : 0,
                                                                                    value: row.is_dynamic
                                                                                        ? row.doctype_field
                                                                                        : row.variable_value,
                                                                                }));

                                                                                const hasEmptyValue = dataList.some(
                                                                                    (row) => !row.value
                                                                                );
                                                                                if (hasEmptyValue) {
                                                                                    frappe.msgprint(
                                                                                        "Please fill in all the Variable Value fields."
                                                                                    );
                                                                                    return;
                                                                                }

                                                                                var currentDateTime =
                                                                                    frappe.datetime.now_datetime();
                                                                                var formattedDateTime = moment(
                                                                                    currentDateTime
                                                                                ).format("DD-MM-YYYY HH:mm:ss");

                                                                                console.log(formattedDateTime);

                                                                                frappe.call({
                                                                                    method:
                                                                                        "whatsapp_app.whatsapp_app.doctype.api.send_whatsapp_message",
                                                                                    args: {
                                                                                        template_name:
                                                                                            values["select_template"],
                                                                                        doctype: doctype,
                                                                                        name: names,
                                                                                        data: dataList,
                                                                                        current_date: formattedDateTime,
                                                                                        number: phone,
                                                                                    },
                                                                                    freeze: true,
                                                                                    callback: (r) => {
                                                                                        var textElement = $("<p>")
                                                                                            .css("padding-right", "10px")
                                                                                            .css("padding-left", "120px")
                                                                                            .css("text-align", "right");
                                                                                        var spanElement = $("<div>")
                                                                                            .css("background-color", "#dcf8c6")
                                                                                            .css("padding", "10px")
                                                                                            .css("padding-bottom", "20px")
                                                                                            .css("border-radius", "10px");

                                                                                        frappe.call({
                                                                                            method: "frappe.client.get_list",
                                                                                            args: {
                                                                                                doctype: "Comment",

                                                                                                fields: ["name", "content"],
                                                                                                limit: 1,
                                                                                                order_by: "creation desc",
                                                                                            },
                                                                                            callback: function (response) {
                                                                                                console.log(response);
                                                                                                if (
                                                                                                    response &&
                                                                                                    response.message &&
                                                                                                    response.message[0]
                                                                                                ) {
                                                                                                    var lastComment =
                                                                                                        response.message[0];
                                                                                                    var lastCommentContent =
                                                                                                        lastComment.content;
                                                                                                    var tempElement =
                                                                                                        document.createElement("div");
                                                                                                    tempElement.innerHTML =
                                                                                                        lastCommentContent;
                                                                                                    var extractedText =
                                                                                                        tempElement.querySelector(
                                                                                                            "a"
                                                                                                        ).innerText;
                                                                                                    console.log(extractedText);
                                                                                                    spanElement.text(extractedText);
                                                                                                }
                                                                                            },
                                                                                        });
                                                                                        spanElement.appendTo(textElement);
                                                                                        textElement.appendTo(messagesDiv);
                                                                                    },
                                                                                    error: (r) => {
                                                                                        frappe.msgprint(
                                                                                            "something went wrong!"
                                                                                        );
                                                                                    },
                                                                                });

                                                                                d1.hide();
                                                                            },
                                                                        });

                                                                        const tableSection = $("<div>").appendTo(
                                                                            d1.body
                                                                        );

                                                                        function renderTable(data) {
                                                                            tableSection.empty();

                                                                            const table = $(
                                                                                '<table class="table table-bordered" id="tabledata">'
                                                                            ).appendTo(tableSection);
                                                                            const thead = $("<thead>").appendTo(table);
                                                                            const tbody = $("<tbody>").appendTo(table);

                                                                            const headerRow = $("<tr>").appendTo(thead);
                                                                            $("<th>")
                                                                                .text("Variable Name")
                                                                                .appendTo(headerRow);
                                                                            $("<th>")
                                                                                .text("Is Dynamic")
                                                                                .appendTo(headerRow);
                                                                            $("<th>")
                                                                                .text("Variable Value")
                                                                                .appendTo(headerRow);

                                                                            data.forEach((row) => {
                                                                                const variableName = row.variable_name;
                                                                                const variableValue = row.variable_value;
                                                                                const isDynamic = row.is_dynamic;
                                                                                const doctypeField = row.doctype_field;

                                                                                const rowElement =
                                                                                    $("<tr>").appendTo(tbody);
                                                                                $("<td>")
                                                                                    .text(variableName)
                                                                                    .appendTo(rowElement);
                                                                                const dynamicCheckbox = $(
                                                                                    '<input type="checkbox">'
                                                                                )
                                                                                    .prop("checked", !!isDynamic)
                                                                                    .appendTo($("<td>").appendTo(rowElement));
                                                                                const variableValueInput =
                                                                                    $("<td>").appendTo(rowElement);
                                                                                if (isDynamic) {
                                                                                    const selectField = $("<select>")
                                                                                        .css({ width: "200px", height: "30px" })
                                                                                        .appendTo(variableValueInput);

                                                                                    customerFields.forEach((field) => {
                                                                                        $("<option>")
                                                                                            .text(field.label)
                                                                                            .val(field.fieldname)
                                                                                            .appendTo(selectField);
                                                                                    });

                                                                                    selectField.val(doctypeField);
                                                                                } else {
                                                                                    $('<input type="text">')
                                                                                        .val(variableValue)
                                                                                        .css({ width: "200px", height: "30px" })
                                                                                        .appendTo(variableValueInput);
                                                                                }

                                                                                dynamicCheckbox.on("change", function () {
                                                                                    const isChecked = $(this).is(":checked");
                                                                                    row.is_dynamic = isChecked ? 1 : 0;
                                                                                    if (isChecked) {
                                                                                        variableValueInput.empty();
                                                                                        const selectField = $("<select>")
                                                                                            .css({
                                                                                                width: "200px",
                                                                                                height: "30px",
                                                                                            })
                                                                                            .appendTo(variableValueInput);

                                                                                        customerFields.forEach((field) => {
                                                                                            $("<option>")
                                                                                                .text(field.label)
                                                                                                .val(field.fieldname)
                                                                                                .appendTo(selectField);
                                                                                        });

                                                                                        selectField.val(doctypeField);
                                                                                        row.doctype_field = doctypeField;
                                                                                    } else {
                                                                                        variableValueInput.empty();
                                                                                        $('<input type="text">')
                                                                                            .val(row.variable_value)
                                                                                            .css({
                                                                                                width: "200px",
                                                                                                height: "30px",
                                                                                            })
                                                                                            .appendTo(variableValueInput);
                                                                                        row.doctype_field = "";
                                                                                    }
                                                                                });

                                                                                variableValueInput.on(
                                                                                    "change",
                                                                                    function () {
                                                                                        const selectedValue = $(this).val();
                                                                                        if (isDynamic) {
                                                                                            row.doctype_field = selectedValue;
                                                                                        } else {
                                                                                            row.variable_value = selectedValue;
                                                                                        }
                                                                                    }
                                                                                );
                                                                            });
                                                                        }

                                                                        function getTableData() {
                                                                            const table = tableSection.find("#tabledata");
                                                                            const data = [];

                                                                            table
                                                                                .find("tbody tr")
                                                                                .each((index, element) => {
                                                                                    const variableName = $(element)
                                                                                        .find("td:nth-child(1)")
                                                                                        .text();
                                                                                    const isDynamic = $(element)
                                                                                        .find('input[type="checkbox"]')
                                                                                        .is(":checked");
                                                                                    const doctypeField = $(element)
                                                                                        .find("select")
                                                                                        .val();
                                                                                    const variableValueInput =
                                                                                        $(element).find('input[type="text"]');
                                                                                    const variableValue = isDynamic
                                                                                        ? doctypeField
                                                                                        : variableValueInput.val();

                                                                                    data.push({
                                                                                        variable_name: variableName,
                                                                                        variable_value: variableValue,
                                                                                        is_dynamic: isDynamic ? 1 : 0,
                                                                                        doctype_field: doctypeField,
                                                                                    });
                                                                                });

                                                                            return data;
                                                                        }

                                                                        d1.show();
                                                                    }
                                                                },
                                                                error: (r) => {
                                                                    frappe.msgprint("something went wrong!");
                                                                },
                                                            });
                                                        }
                                                    },
                                                    error: (r) => {
                                                        frappe.msgprint("something went wrong!");
                                                    },
                                                });
                                                function extractDynamicVariables(templateSample) {
                                                    const regex = /{{([^{}]+)}}/g;
                                                    const matches = [];
                                                    let match;

                                                    while ((match = regex.exec(templateSample)) !== null) {
                                                        matches.push(match[1]);
                                                    }

                                                    return matches;
                                                }
                                            });

                                            buttonElement.click(function () {
                                                var message = inputElement.val();

                                                if (message) {
                                                    var currentDateTime = frappe.datetime.now_datetime();
                                                    var formattedDateTime = moment(currentDateTime).format(
                                                        "DD-MM-YYYY HH:mm:ss"
                                                    );
                                                    frappe.call({
                                                        method:
                                                            "whatsapp_app.whatsapp_app.doctype.api.send_whatsapp_message",
                                                        args: {
                                                            number: phone,
                                                            message: message,
                                                            current_date: formattedDateTime,
                                                        },
                                                        callback: function (response) {
                                                            console.log(response.message);
                                                            inputElement.val("");

                                                            var textElement = $("<p>")
                                                                .css("padding-right", "10px")
                                                                .css("padding-left", "120px")
                                                                .css("text-align", "right");
                                                            var spanElement = $("<div>")
                                                                .css("background-color", "#dcf8c6")
                                                                .css("padding", "10px")
                                                                .css("padding-bottom", "20px")
                                                                .css("border-radius", "10px");

                                                            spanElement.text(message);
                                                            spanElement.appendTo(textElement);
                                                            textElement.appendTo(messagesDiv);
                                                        },
                                                    });
                                                }
                                            });
                                        },
                                    });



                                } else {

                                    container.empty();
                                    headingDiv.appendTo(container);
                                    messagesDiv.appendTo(container);

                                    messagesDiv.empty();
                                    allElement.appendTo(container);

                                    setTimeout(function () {
                                        messagesDiv.scrollTop(messagesDiv[0].scrollHeight);
                                    }, 0);

                                    closeButtonElement.on("click", function () {
                                        container.hide();
                                    });

                                    if (showButtonClicked) {
                                        container.show();
                                        showButtonClicked = true;
                                    }


                                    frappe.call({
                                        method:
                                            "whatsapp_app.whatsapp_app.doctype.api.check_status",
                                        args: {
                                            number: phone,
                                        },
                                        callback: function (response) {
                                            if (response.message === "yes") {
                                                buttonElement1.appendTo(allElement);
                                                inputElement.appendTo(allElement);
                                                buttonElement.appendTo(allElement);
                                            } else {
                                                if (!expiredMessageAdded) {
                                                    statusElement = $("<p>")
                                                        .css("color", "black")
                                                        .css("margin-top", "5px")
                                                        .css("width", "100%")
                                                        .css("text-align", "center")
                                                        .text("The chat has been expired")
                                                        .appendTo(allElement);
                                        
                                                        expiredMessageAdded = true; 
                                                }
                                                buttonElement1.prependTo(allElement);
                                                buttonElement.appendTo(allElement);
                                            }
                                        },
                                    });

                                    buttonElement1.click(function () {
                                        
                                        container.children().css('opacity', '0.6');
                                        
                                        var names = cur_frm.doc.name;
                                        frappe.call({
                                            method:
                                                "whatsapp_app.whatsapp_app.doctype.api.get_template_list",
                                            args: {
                                                doctype: doctype,
                                            },
                                            callback: (r) => {
                                                if (r.message) {
                                                    const template = r.message;

                                                    frappe.call({
                                                        method: "frappe.client.get_list",
                                                        args: {
                                                            doctype: "Templates",
                                                            filters: {
                                                                name: ["in", template],
                                                            },
                                                            fields: ["name", "status", "sample"],
                                                            limit_start: 0,
                                                            limit_page_length: 0,
                                                        },

                                                        callback: function (response) {
                                                            if (response.message) {
                                                                const templateData = response.message;
                                                                const customerDoctype = doctype;
                                                                const customerFields = frappe
                                                                    .get_meta(customerDoctype)
                                                                    .fields.filter((field) => {
                                                                        return (
                                                                            field.fieldtype !== "Column Break" &&
                                                                            field.fieldtype !== "Section Break"
                                                                        );
                                                                    })
                                                                    .map((field) => {
                                                                        return {
                                                                            fieldname: field.fieldname,
                                                                            label: field.label,
                                                                        };
                                                                    });

                                                                const customerFieldLabels = customerFields.map(
                                                                    (fieldname) => {
                                                                        const fieldMeta = frappe
                                                                            .get_meta(doctype)
                                                                            .fields.find(
                                                                                (field) => field.fieldname === fieldname
                                                                            );
                                                                        return fieldMeta
                                                                            ? fieldMeta.label
                                                                            : fieldname;
                                                                    }
                                                                );

                                                                const d1 = new frappe.ui.Dialog({
                                                                    title: "Send Message",
                                                                    fields: [
                                                                        {
                                                                            label: "Select Template",
                                                                            fieldname: "select_template",
                                                                            fieldtype: "Select",
                                                                            options: template,
                                                                            onchange: function () {
                                                                                const selectedValue = this.get_value();
                                                                                const previousValue = this.last_value;
                                                                                if (
                                                                                    selectedValue &&
                                                                                    selectedValue !== previousValue
                                                                                ) {
                                                                                    this.last_value = selectedValue;
                                                                                    const selectedTemplateData =
                                                                                        templateData.find(
                                                                                            (template) =>
                                                                                                template.name === selectedValue
                                                                                        );
                                                                                    if (selectedTemplateData) {
                                                                                        const dynamicVariables =
                                                                                            extractDynamicVariables(
                                                                                                selectedTemplateData.sample
                                                                                            );

                                                                                        const variableData =
                                                                                            dynamicVariables.map(
                                                                                                (variable) => ({
                                                                                                    variable_name: variable,
                                                                                                    variable_value: "",
                                                                                                    is_dynamic: 0,
                                                                                                    doctype_field: "",
                                                                                                })
                                                                                            );

                                                                                        renderTable(variableData);
                                                                                    }
                                                                                }
                                                                            },
                                                                        },
                                                                    ],
                                                                    primary_action_label: "Send",

                                                                    primary_action(values) {
                                                                        const tableData = getTableData();
                                                                        const dataList = tableData.map((row) => ({
                                                                            name: row.variable_name,
                                                                            is_dynamic: row.is_dynamic ? 1 : 0,
                                                                            value: row.is_dynamic
                                                                                ? row.doctype_field
                                                                                : row.variable_value,
                                                                        }));

                                                                        const hasEmptyValue = dataList.some(
                                                                            (row) => !row.value
                                                                        );
                                                                        if (hasEmptyValue) {
                                                                            frappe.msgprint(
                                                                                "Please fill in all the Variable Value fields."
                                                                            );
                                                                            return;
                                                                        }

                                                                        var currentDateTime =
                                                                            frappe.datetime.now_datetime();
                                                                        var formattedDateTime = moment(
                                                                            currentDateTime
                                                                        ).format("DD-MM-YYYY HH:mm:ss");

                                                                        console.log(formattedDateTime);

                                                                        frappe.call({
                                                                            method:
                                                                                "whatsapp_app.whatsapp_app.doctype.api.send_whatsapp_message",
                                                                            args: {
                                                                                template_name:
                                                                                    values["select_template"],
                                                                                doctype: doctype,
                                                                                name: names,
                                                                                data: dataList,
                                                                                current_date: formattedDateTime,
                                                                                number: phone,
                                                                            },
                                                                            freeze: true,
                                                                            callback: (r) => {
                                                                                var textElement = $("<p>")
                                                                                    .css("padding-right", "10px")
                                                                                    .css("padding-left", "120px")
                                                                                    .css("text-align", "right");
                                                                                var spanElement = $("<div>")
                                                                                    .css("background-color", "#dcf8c6")
                                                                                    .css("padding", "10px")
                                                                                    .css("padding-bottom", "20px")
                                                                                    .css("border-radius", "10px");

                                                                                frappe.call({
                                                                                    method: "frappe.client.get_list",
                                                                                    args: {
                                                                                        doctype: "Comment",

                                                                                        fields: ["name", "content"],
                                                                                        limit: 1,
                                                                                        order_by: "creation desc",
                                                                                    },
                                                                                    callback: function (response) {
                                                                                        console.log(response);
                                                                                        if (
                                                                                            response &&
                                                                                            response.message &&
                                                                                            response.message[0]
                                                                                        ) {
                                                                                            var lastComment =
                                                                                                response.message[0];
                                                                                            var lastCommentContent =
                                                                                                lastComment.content;
                                                                                            var tempElement =
                                                                                                document.createElement("div");
                                                                                            tempElement.innerHTML =
                                                                                                lastCommentContent;
                                                                                            var extractedText =
                                                                                                tempElement.querySelector(
                                                                                                    "a"
                                                                                                ).innerText;
                                                                                            console.log(extractedText);
                                                                                            spanElement.text(extractedText);
                                                                                        }
                                                                                    },
                                                                                });
                                                                                spanElement.appendTo(textElement);
                                                                                textElement.appendTo(messagesDiv);
                                                                            },
                                                                            error: (r) => {
                                                                                frappe.msgprint(
                                                                                    "something went wrong!"
                                                                                );
                                                                            },
                                                                        });

                                                                        d1.hide();
                                                                    },
                                                                });

                                                                const tableSection = $("<div>").appendTo(
                                                                    d1.body
                                                                );

                                                                function renderTable(data) {
                                                                    tableSection.empty();

                                                                    const table = $(
                                                                        '<table class="table table-bordered" id="tabledata">'
                                                                    ).appendTo(tableSection);
                                                                    const thead = $("<thead>").appendTo(table);
                                                                    const tbody = $("<tbody>").appendTo(table);

                                                                    const headerRow = $("<tr>").appendTo(thead);
                                                                    $("<th>")
                                                                        .text("Variable Name")
                                                                        .appendTo(headerRow);
                                                                    $("<th>")
                                                                        .text("Is Dynamic")
                                                                        .appendTo(headerRow);
                                                                    $("<th>")
                                                                        .text("Variable Value")
                                                                        .appendTo(headerRow);

                                                                    data.forEach((row) => {
                                                                        const variableName = row.variable_name;
                                                                        const variableValue = row.variable_value;
                                                                        const isDynamic = row.is_dynamic;
                                                                        const doctypeField = row.doctype_field;

                                                                        const rowElement =
                                                                            $("<tr>").appendTo(tbody);
                                                                        $("<td>")
                                                                            .text(variableName)
                                                                            .appendTo(rowElement);
                                                                        const dynamicCheckbox = $(
                                                                            '<input type="checkbox">'
                                                                        )
                                                                            .prop("checked", !!isDynamic)
                                                                            .appendTo($("<td>").appendTo(rowElement));
                                                                        const variableValueInput =
                                                                            $("<td>").appendTo(rowElement);
                                                                        if (isDynamic) {
                                                                            const selectField = $("<select>")
                                                                                .css({ width: "200px", height: "30px" })
                                                                                .appendTo(variableValueInput);

                                                                            customerFields.forEach((field) => {
                                                                                $("<option>")
                                                                                    .text(field.label)
                                                                                    .val(field.fieldname)
                                                                                    .appendTo(selectField);
                                                                            });

                                                                            selectField.val(doctypeField);
                                                                        } else {
                                                                            $('<input type="text">')
                                                                                .val(variableValue)
                                                                                .css({ width: "200px", height: "30px" })
                                                                                .appendTo(variableValueInput);
                                                                        }

                                                                        dynamicCheckbox.on("change", function () {
                                                                            const isChecked = $(this).is(":checked");
                                                                            row.is_dynamic = isChecked ? 1 : 0;
                                                                            if (isChecked) {
                                                                                variableValueInput.empty();
                                                                                const selectField = $("<select>")
                                                                                    .css({
                                                                                        width: "200px",
                                                                                        height: "30px",
                                                                                    })
                                                                                    .appendTo(variableValueInput);

                                                                                customerFields.forEach((field) => {
                                                                                    $("<option>")
                                                                                        .text(field.label)
                                                                                        .val(field.fieldname)
                                                                                        .appendTo(selectField);
                                                                                });

                                                                                selectField.val(doctypeField);
                                                                                row.doctype_field = doctypeField;
                                                                            } else {
                                                                                variableValueInput.empty();
                                                                                $('<input type="text">')
                                                                                    .val(row.variable_value)
                                                                                    .css({
                                                                                        width: "200px",
                                                                                        height: "30px",
                                                                                    })
                                                                                    .appendTo(variableValueInput);
                                                                                row.doctype_field = "";
                                                                            }
                                                                        });

                                                                        variableValueInput.on(
                                                                            "change",
                                                                            function () {
                                                                                const selectedValue = $(this).val();
                                                                                if (isDynamic) {
                                                                                    row.doctype_field = selectedValue;
                                                                                } else {
                                                                                    row.variable_value = selectedValue;
                                                                                }
                                                                            }
                                                                        );
                                                                    });
                                                                }

                                                                function getTableData() {
                                                                    const table = tableSection.find("#tabledata");
                                                                    const data = [];

                                                                    table
                                                                        .find("tbody tr")
                                                                        .each((index, element) => {
                                                                            const variableName = $(element)
                                                                                .find("td:nth-child(1)")
                                                                                .text();
                                                                            const isDynamic = $(element)
                                                                                .find('input[type="checkbox"]')
                                                                                .is(":checked");
                                                                            const doctypeField = $(element)
                                                                                .find("select")
                                                                                .val();
                                                                            const variableValueInput =
                                                                                $(element).find('input[type="text"]');
                                                                            const variableValue = isDynamic
                                                                                ? doctypeField
                                                                                : variableValueInput.val();

                                                                            data.push({
                                                                                variable_name: variableName,
                                                                                variable_value: variableValue,
                                                                                is_dynamic: isDynamic ? 1 : 0,
                                                                                doctype_field: doctypeField,
                                                                            });
                                                                        });

                                                                    return data;
                                                                }

                                                                d1.show();
                                                            }
                                                        },
                                                        error: (r) => {
                                                            frappe.msgprint("something went wrong!");
                                                        },
                                                    });
                                                }
                                            },
                                            error: (r) => {
                                                frappe.msgprint("something went wrong!");
                                            },
                                        });
                                        function extractDynamicVariables(templateSample) {
                                            const regex = /{{([^{}]+)}}/g;
                                            const matches = [];
                                            let match;

                                            while ((match = regex.exec(templateSample)) !== null) {
                                                matches.push(match[1]);
                                            }

                                            return matches;
                                        }
                                    });
                                    buttonElement.click(function () {
                                        var message = inputElement.val();

                                        if (message) {
                                            var currentDateTime = frappe.datetime.now_datetime();
                                            var formattedDateTime = moment(currentDateTime).format(
                                                "DD-MM-YYYY HH:mm:ss"
                                            );
                                            frappe.call({
                                                method:
                                                    "whatsapp_app.whatsapp_app.doctype.api.send_whatsapp_message",
                                                args: {
                                                    number: phone,
                                                    message: message,
                                                    current_date: formattedDateTime,
                                                },
                                                callback: function (response) {
                                                    console.log(response.message);
                                                    inputElement.val("");

                                                    var textElement = $("<p>")
                                                        .css("padding-right", "10px")
                                                        .css("padding-left", "120px")
                                                        .css("text-align", "right");
                                                    var spanElement = $("<div>")
                                                        .css("background-color", "#dcf8c6")
                                                        .css("padding", "10px")
                                                        .css("padding-bottom", "20px")
                                                        .css("border-radius", "10px");

                                                    spanElement.text(message);
                                                    spanElement.appendTo(textElement);
                                                    textElement.appendTo(messagesDiv);
                                                },
                                            });
                                        }
                                    });
                                }



                            }
                        });
                    }
                );
            }
        }

        function adjustContainerStyles() {
            if (window.innerWidth < 499) {
                container.css({
                    width: "80%",
                    right: "10%",
                });
            } else if (window.innerWidth >= 499 && window.innerWidth < 530) {
                container.css({
                    width: "40%",
                    right: "5%",
                });
            } else if (window.innerWidth >= 530 && window.innerWidth < 800) {
                container.css({
                    width: "40%",
                    right: "5%",
                });
            } else if (window.innerWidth >= 800 && window.innerWidth < 798) {
                container.css({
                    width: "30%",
                    right: "5%",
                });
            } else if (window.innerWidth >= 798 && window.innerWidth < 838) {
                container.css({
                    width: "30%",
                    right: "5%",
                });
            } else if (window.innerWidth >= 838 && window.innerWidth < 1300) {
                container.css({
                    width: "30%",
                    right: "5%",
                });
                inputElement.css({
                    width: "40%",
                });
            } else {
                container.css({
                    width: "20%",
                    right: "80px",
                    height: "65%",
                });
            }
        }

        $(window).resize(adjustContainerStyles);

        adjustContainerStyles();
    },
});
