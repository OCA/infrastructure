# © 2015-2019 Elico Corp (https://www.elico-corp.com).
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
from odoo import models, fields


class DNSDomain(models.Model):
    _name = 'dns.domain'
    _inherit = 'dns.binding'
    _description = 'DNS Domain'

    name = fields.Char(
        string='Domain',
        required=True,
        help='Domain name without "www", such as "dnspod.cn"'
    )
    state = fields.Selection([
        ('draft', 'Draft'),
        ('done', 'Done'),
        ('exception', 'Exception')],
        string='State',
        default='draft',
        help='Done when succeed otherwise Exception')
    record_ids = fields.One2many(
        comodel_name='dns.record',
        inverse_name='domain_id',
        string='Subdomains'
    )

    _sql_constraints = [
        ('dns_domain_uniq', 'unique(external_id)',
         "An external_id already exists with the same record."),
    ]
