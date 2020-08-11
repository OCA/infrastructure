# Copyright (C) 2020 Open Source Integrators
# Copyright (C) 2020 Serpent Consulting Services Pvt. Ltd.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

{
    "name": "Openshift Connector",
    "summary": """Openshift Connector""",
    "version": "13.0.1.0.0",
    "license": "AGPL-3",
    "author": "Odoo Community Association (OCA), Open Source Integrators",
    "website": "https://github.com/OCA/infrastructure",
    "category": "Tools",
    "depends": ["connector"],
    "data": ["security/ir.model.access.csv", "views/backend_openshift_view.xml"],
    "installable": True,
    "maintainers": ["max3903"],
    "development_status": "Beta",
}
