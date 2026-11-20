# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Contract link to DNS informations",
    "version": "18.0.1.0.0",
    "category": "Services",
    "application": True,
    "external_dependencies": {
        "python": ["validator-collection"],
    },
    "depends": ["base_dns_infrastructure", "contract"],
    "author": "Mind And Go, " "Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "website": "https://github.com/OCA/infrastructure",
    "data": [
        "views/contract.xml",
        "views/dns_record.xml",
        "views/dns_domain_zone.xml",
    ],
    "demo": [],
    "installable": True,
}
