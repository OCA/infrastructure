# © 2015-2019 Elico Corp (https://www.elico-corp.com).
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
from odoo.addons.component.core import AbstractComponent


class DNSAbstractAdapter(AbstractComponent):
    _name = 'dns.abstract.adapter'
    _inherit = ['base.backend.adapter', 'base.dns.connector']
    _usage = 'backend.adapter'

    def search_all(self, domain_id):
        raise NotImplementedError

    def search(self, external_id):
        raise NotImplementedError

    def create(self):
        raise NotImplementedError

    def write(self, external_id):
        raise NotImplementedError

    def unlink(self, external_id):
        raise NotImplementedError
