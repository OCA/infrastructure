from odoo.addons.component.core import AbstractComponent


class DNSAbstractDeleter(AbstractComponent):
    _name = 'dns.abstract.deleter'
    _inherit = 'base.deleter'
    _usage = 'dns.deleter'

    def run(self, binding):
        self._before_delete()
        self.backend_adapter.delete(binding)
        self._after_delete()

    def _before_delete(self):
        return

    def _after_delete(self):
        return
