# Copyright 2015 Elico Corp
# Copyright 2016 LasLabs Inc.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Base module for DNS infrastructure",
    "version": "16.0.1.0.0",
    "category": "Connector",
    "external_dependencies": {
        "python": ["validator-collection"],
    },
    "depends": ["base"],
    "author": "Elico Corp, "
    "LasLabs, "
    "Mind And Go, "
    "Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "website": "https://github.com/OCA/infrastructure",
    "data": [
        # "views/dns_backend.xml",
        # "views/dns_record.xml",
        # "views/dns_zone.xml",
        # "views/dns_menu.xml",
        # "views/connector_config_settings.xml",
        "data/dns_record_type.xml",
        # "security/dns.xml",
        # "security/ir.model.access.csv",
    ],
    "installable": True,
}
