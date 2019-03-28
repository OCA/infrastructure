from odoo.addons.component.core import AbstractComponent


class DNSAbstractAdapter(AbstractComponent):
    _name = 'dns.abstract.adapter'
    _inherit = ['base.backend.adapter', 'base.dns.connector']
    _usage = 'backend.adapter'

    def search(self, domain_id):
        raise NotImplementedError

    def send_request(self, external_id):
        raise NotImplementedError
