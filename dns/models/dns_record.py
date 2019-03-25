# © 2019 Elico Corp (https://www.elico-corp.com).
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
from odoo import models, fields, api


class DNSRecord(models.Model):
    _name = 'dns.record'
    _description = 'DNS records'

    @api.model
    def _line_select_version(self):
        return []

    @api.model
    def _type_select_version(self):
        return []

    name = fields.Char(
        'Subdomain',
        help='Host record, such as "www"',
        required=True)
    domain_id = fields.Many2one(
        comodel_name='dns.domain',
        string="Domain",
        ondelete='cascade')
    type = fields.Selection(
        selection='_type_select_version',
        string='Record Type'
    )
    line = fields.Selection(
        selection='_line_select_version',
        string='Record Line'
    )
    value = fields.Text(
        string='Value',
        help="such as IP:200.200.200.200",
        required=True
    )
    mx_priority = fields.Integer(
        string='MX priority',
        help="scope: 1-20",
        default=1
    )
    ttl = fields.Integer(
        string='TTL',
        default=600,
        help="scope: 1-604800",
        required=True
    )
    backend_id = fields.Many2one(
        comodel_name='dns.backend',
        related='domain_id.backend_id',
        store=True
    )
