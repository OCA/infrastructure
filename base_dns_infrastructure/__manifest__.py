# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Base module for DNS infrastructure",
    "version": "16.0.1.0.1",
    "category": "Services",
    "application": True,
    "external_dependencies": {
        "python": ["validator-collection"],
    },
    "depends": ["base", "mail"],
    "author": "Elico Corp, "
    "LasLabs, "
    "Mind And Go, "
    "Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "website": "https://github.com/OCA/infrastructure",
    "data": [
        "data/dns_record_type.xml",
        "views/dns_record_type.xml",
        "views/dns_record.xml",
        "views/dns_domain_zone.xml",
        "views/dns_menu.xml",
        "security/dns.xml",
        "security/ir.model.access.csv",
    ],
    "demo": ["demo/base_dns_infrastructure.xml"],
    "installable": True,
}
