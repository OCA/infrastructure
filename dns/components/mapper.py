from odoo.addons.component.core import AbstractComponent


class DNSAbstractImportMapper(AbstractComponent):
    _name = 'dns.abstract.mapper'
    _inherit = ['base.dns.connector', 'base.import.mapper']
    _usage = 'import.mapper'
