# -*- coding: utf-8 -*-
from odoo import api, fields, models
from odoo.addons.queue_job.job import job,related_action


class DNSBingingAbstract(models.Model):
    _name = 'dns.binding'
    _description = 'DNS binding'
    _inherits = {'dns.record': 'odoo_id'}

    odoo_id = fields.Many2one('dns.record', required=True, ondelete='cascade')
    backend_id = fields.Many2one('dns.backend')
    external_id = fields.Char()
    sync_date = fields.Datetime()
    # FIXME: _sql_constraints for odoo_id and backend_id unique.

    @job(default_channel='root')
    def sync_dns_records(self, signal):
        with self.backend_id.work_on(self._name) as work:
            syncer = work.component(usage='dns.importer')
            return syncer.run(self.id, signal)
