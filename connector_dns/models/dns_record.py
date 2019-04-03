# © 2019 Elico Corp (https://www.elico-corp.com).
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
from odoo import models, fields, api


class DNSRecord(models.Model):
    _name = 'dns.record'
    _description = 'DNS records'

    name = fields.Char(
        'Subdomain',
        help='Host record, such as "www"',
        required=True)
    domain_id = fields.Many2one(
        comodel_name='dns.domain',
        domain="[('state', '=', 'done')]",
        string='Domain',
        ondelete='cascade')
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
