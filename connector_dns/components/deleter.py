# © 2019 Elico Corp (https://www.elico-corp.com).
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
from odoo.addons.component.core import AbstractComponent


class DNSAbstractDeleter(AbstractComponent):
    _name = 'dns.abstract.deleter'
    _inherit = 'base.deleter'
    _usage = 'dns.deleter'

    def run(self, binding):
        self._before_delete(binding)
        self.backend_adapter.delete(binding)
        self._after_delete()

    def _before_delete(self, binding):
        return

    def _after_delete(self):
        return
