from odoo.addons.component.core import AbstractComponent


class DNSAbstractExporter(AbstractComponent):
    _name = 'dns.abstract.exporter'
    _inherit = ['base.exporter', 'base.dns.connector']
    _usage = 'dns.exporter'

    def __init__(self, work_context):
        super(DNSAbstractExporter, self).__init__(work_context)
        self.binding = None
        self.external_id = None

    def run(self, binding):
        self.binding = binding
        self.external_id = self.binder.to_external(self.binding)
        self._before_export()
        if self.external_id:
            self.backend_adapter.write(self.external_id)
        else:
            response = self.backend_adapter.create()
            self.external_id = self._get_external_id(response)
        self.binder.bind(self.external_id, self.binding)
        self._after_export()

    def _before_export(self):
        return

    def _after_export(self):
        return

    def _get_external_id(self, response):
        raise NotImplementedError
