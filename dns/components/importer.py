# -*- coding: utf-8 -*-
from odoo.addons.component.core import AbstractComponent


class DNSAbstractImporter(AbstractComponent):
    _name = 'dns.abstract.importer'
    _inherit = 'base.importer'
    _usage = 'dns.importer'
    _collection = 'dns.backend'
    _apply_on = ['dns.binding']

    def __init__(self, work_context):
        super(DNSAbstractImporter, self).__init__(work_context)
        self.binding_id = None
        self.dns_record = None

    def _before_import(self):
        return

    def _after_import(self):
        return

    def _send_request(self, signal):
        """
        Send request to the DNS provider
        :param signal: Signal of the action
        """
        raise NotImplementedError

    def _validate_data(self, data):
        return

    def _map_data(self):
        return self.mapper.map_record(self.dns_record)

    def _get_binding(self):
        return self.model.browse(self.binding_id)

    def _update_data(self, map_record, **kwargs):
        return map_record.values(**kwargs)

    def _update(self, binding, data):
        self._validate_data(data)
        binding.with_context(no_connector_export=True).write(data)

    def run(self, binding_id, signal):
        self.binding_id = binding_id
        try:
            self.dns_record = self._send_request(signal)
        except Exception:
            return 'No response'

        binding = self._get_binding()
        self._before_import()
        map_record = self._map_data()
        record = self._update_data(map_record)
        self._update(binding, record)
        # FIXME: bind the external id not binding_id
        self.binder.bind(self.binding_id, binding)
        self._after_import()
