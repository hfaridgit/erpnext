<h3>{{_("Official Document")}}</h3>

<p>{{ doc.document_type }}</p>

<h4>{{_("Details")}}</h4>
{{_("Document Number")}}: {{ frappe.utils.get_link_to_form(doc.doctype, doc.name) }}
<br>{{_("For Employee")}}: {{ doc.employee_name }}
<br>{{_("Will Expire On")}}: {{ doc.expiry_date }}
<br>{{ doc.description }}
