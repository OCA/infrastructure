# © 2019 Elico Corp (https://www.elico-corp.com).
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
from odoo import api, fields, models
from odoo.addons.queue_job.job import job, related_action


class DNSBingingAbstract(models.AbstractModel):
    _name = 'dns.binding'
    _inherit = 'external.binding'
    _description = 'DNS binding (abstract)'

    # odoo_id = odoo-side id must be declared in concrete model
    backend_id = fields.Many2one(
        'dns.backend',
        string='DNS Backend',
        required=True,
        ondelete='restrict')
    external_id = fields.Char('ID on DNS Provider')
    sync_date = fields.Datetime('Sync Date')

    _sql_constraints = [
        ('dns_uniq', 'unique(backend_id, external_id)',
         "A binding already exists with the same record."),
    ]

    @job(default_channel='root')
    @api.model
    def sync_dns_domains(self, backend_id, domain_id, signal=None,
                         record_id=None):
        with backend_id.work_on(self._name) as work:
            syncer = work.component(usage='dns.importer')
            return syncer.run(domain_id, signal, record_id)

    @job(default_channel='root')
    @api.model
    def sync_dns_records(self, backend_id, domain_id, signal=None,
                         record_id=None):
        with backend_id.work_on(self._name) as work:
            syncer = work.component(usage='dns.importer')
            return syncer.run(domain_id, signal, record_id)
