# -*- coding: utf-8 -*-
from odoo import models, fields, api


class DNSBackend(models.Model):
    _name = 'dns.backend'
    _inherit = 'connector.backend'
    _description = 'DNS Connector Backend'

    @api.model
    def _selection_version(self):
        return [('1', '1')]

    login = fields.Char()
    password = fields.Char()
    uri = fields.Char()
    version = fields.Selection(_selection_version)
    company_id = fields.Many2one('res.company')
    is_default = fields.Boolean()
    import_date = fields.Datetime()
    export_date = fields.Datetime()

    def sync(self, model, external_id):
        self.ensure_one()
        self.env[model].with_delay().sync_dns_records(self, external_id)


class DNSRecord(models.Model):
    _name = 'dns.record'
    _description = 'DNS records'

    name = fields.Char()
    dns_binding_ids = fields.One2many('dns.binding', inverse_name='odoo_id')
