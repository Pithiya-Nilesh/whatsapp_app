from . import __version__ as app_version

app_name = "whatsapp_app"
app_title = "Whatsapp App"
app_publisher = "Nilesh Pithiya"
app_description = "This App Can send whatsapp messages "
app_icon = "octicon octicon-file-directory"
app_color = "grey"
app_email = "sanskartechnolabtest@gmail.com"
app_license = "MIT"

# Includes in <head>
# ------------------

fixtures = [
    
    #  {"dt":"Client Script","filters":[
    #     [
    #         "module","in",[
    #            "Whatsapp App"
    #         ]
    #     ]
    # ]},
    {"dt": "DocPerm", "filters": [["name", "in", ["WhatsApp Manager"]]]},
]

doctype_js = {
    "Lead" : "public/js/lead.js",
    "Supplier" : "public/js/supplier.js",
    "Opportunity" : "public/js/opportunity.js",
    "Customer": "public/js/customer.js",
    "Raw Data": "public/js/raw_data.js",
    "Item": "public/js/item.js",
    "List of WhatsApp Messages to be Sent": "public/js/list_of_messages_to_be_sent.js"
}
doctype_list_js = {
    "Lead" : "public/js/lead_list.js",
    "Supplier" : "public/js/supplier_list.js",
    "Opportunity" : "public/js/opportunity_list.js",
    "Customer": "public/js/customer_list.js",
    "Raw Data": "public/js/raw_data_list.js",
    "Item": "public/js/item_list.js",
}

# include js, css files in header of desk.html
# app_include_css = "/assets/whatsapp_app/css/whatsapp_app.css"
# app_include_js = "/assets/whatsapp_app/js/whatsapp_app.js"

# include js, css files in header of web template
# web_include_css = "/assets/whatsapp_app/css/whatsapp_app.css"
# web_include_js = "/assets/whatsapp_app/js/whatsapp_app.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "whatsapp_app/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
#	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Installation
# ------------

# before_install = "whatsapp_app.install.before_install"
# after_install = "whatsapp_app.install.after_install"

# Uninstallation
# ------------

# before_uninstall = "whatsapp_app.uninstall.before_uninstall"
# after_uninstall = "whatsapp_app.uninstall.after_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "whatsapp_app.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# DocType Class
# ---------------
# Override standard doctype classes

# override_doctype_class = {
# 	"ToDo": "custom_app.overrides.CustomToDo"
# }

# Document Events
# ---------------
# Hook on document methods and events

# doc_events = {
# 	"*": {
# 		"validate": "whatsapp_app.whatsapp_app.custom.users.allow_whatsapp_welcome_message"
# 	# 	"on_update": "method",
# 	# 	"on_cancel": "method",
# 	# 	"on_trash": "method"
# 	}
# }

# Scheduled Tasks
# ---------------

scheduler_events = {
    # "send_insurance_reminder": {
    #    "0 10 * * 1": [
    #       "whatsapp_app.whatsapp_app.doctype.api.generate_pdf_and_store_data"
    #     ]
    # },

    "delete_insurance_reminder_pdf": {
       "0 0 1,15 * *": [
          "whatsapp_app.whatsapp_app.doctype.api.delete_sent_file"
        ]
    },

    "send_insurance_reminder_daily_create_pdf": {
       "0 10 * * *": [
          "whatsapp_app.whatsapp_app.doctype.api.generate_pdf_and_store_data"
        ]
    },

    # "send_insurance_reminder_daily_from_list": {
    #    "0 11 * * *": [
    #       "whatsapp_app.whatsapp_app.doctype.api.send_whatsapp_reminder_using_scheduler"
    #     ]
    # },
    
    # "send_remider_if_not_repliyed": {
    #    "0 11 * * *": [
    #       "whatsapp_app.whatsapp_app.doctype.api.send_remider_if_not_repliyed"
    #     ]
    # },

    # "send_insurance_reminder": {
    #    "0 10 * * 1": [
    #       "whatsapp_app.whatsapp_app.doctype.api.create_table"
    #     ]
    # },
    # "delete_insurance_reminder_pdf": {
    #    "0 0 1,15 * *": [
    #       "whatsapp_app.whatsapp_app.doctype.api.delete_sent_file"
    #     ]
    # },
    # "whatsapp_message_report": {
    #     "* * * * *": [
    #         "whatsapp_app.task.send_report_on_whatsapp"
    #     ]
    # },
    # "whatsapp_queue_message": {
    #     "* 12 * * *": [
    #         # "whatsapp_app.task.send_register_message"
    #         "whatsapp_app.whatsapp_app.doctype.api.send_insurance_expiry_reminder_notification"
    #     ]
    # },

    # 	"all": [
    # 		"whatsapp_app.tasks.all"
    # 	],
    	# "daily": [
    	# 	"whatsapp_app.whatsapp_app.doctype.api.send_insurance_expiry_reminder_notification",
   		# "whatsapp_app.whatsapp_app.doctype.api.send_fitness_expiry_reminder_notification",
    	# ]
    # 	"hourly": [
    # 		"whatsapp_app.tasks.hourly"
    # 	],
    # 	"weekly": [
    # 		"whatsapp_app.tasks.weekly"
    # 	]
    # 	"monthly": [
    # 		"whatsapp_app.tasks.monthly"
    # 	]
}


# Testing
# -------

# before_tests = "whatsapp_app.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "whatsapp_app.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "whatsapp_app.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]


# User Data Protection
# --------------------

user_data_fields = [
    {
        "doctype": "{doctype_1}",
        "filter_by": "{filter_by}",
        "redact_fields": ["{field_1}", "{field_2}"],
        "partial": 1,
    },
    {
        "doctype": "{doctype_2}",
        "filter_by": "{filter_by}",
        "partial": 1,
    },
    {
        "doctype": "{doctype_3}",
        "strict": False,
    },
    {
        "doctype": "{doctype_4}"
    }
]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
# 	"whatsapp_app.auth.validate"
# ]

# Translation
# --------------------------------

# Make link fields search translated document names for these DocTypes
# Recommended only for DocTypes which have limited documents with untranslated names
# For example: Role, Gender, etc.
# translated_search_doctypes = []


# additional_timeline_content = {
#     "*": ["whatsapp_app.api.get_linked_call_logs"]
# }

# additional_timeline_content = {
#     # show in each document's timeline
#     "*": ["frappe.desk.doctype.todo.todo.all_timeline"]
#     # only show in ToDo's timeline
#     # "ToDo": ["app.timeline.todo_timeline"]
# }
