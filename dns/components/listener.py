# -*- coding: utf-8 -*-
from odoo.addons.component.core import Component
from odoo.addons.component_event import skip_if
import uuid


class DNSRecordListener(Component):
    _name = 'dns.record.listener'
    _inherit = 'base.connector.listener'
    _apply_on = ['dns.record']

    @skip_if(lambda self, record, **kwargs: self.no_connector_export(record))
    def on_record_write(self, record, fields=None):
        for binding in record.dns_binding_ids:
            binding.with_delay().sync_dns_records(binding, 'write')

    @skip_if(lambda self, record, **kwargs: self.no_connector_export(record))
    def on_record_create(self, record, fields=None):
        self.env['dns.binding'].create({
            'backend_id': 1,
            'odoo_id': record.id,
            'external_id': str(uuid.uuid4())
        })
        for binding in record.dns_binding_ids:
            binding.with_delay().sync_dns_records(binding, 'create')
