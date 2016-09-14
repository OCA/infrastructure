# -*- coding: utf-8 -*-
# Copyright 2016 LasLabs Inc.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, fields, api


class DNSRecordTypeBind(models.Model):
    _name = 'dns.record.type.bind'
    _description = 'DNS Record Type Binding'
    _inherit = 'dns.binding'
    _inherits = {'dns.record.type': 'odoo_id'}

    odoo_id = fields.Many2one(
        comodel_name='dns.record.type',
        string='DNS Record',
        required=True,
        ondelete='cascade',
    )


class DNSRecordType(models.Model):
    _name = 'dns.record.type'
    _description = 'DNS Record Type'

    name = fields.Char(
        required=True,
        help='Name of DNS record type, such a "A" or "CNAME".',
    )
    code = fields.Char(
        required=True,
    )
    help = fields.Text(
        help="Text that will be displayed to user as a formatting guide "
             "for this record type.",
    )
    validate_regex = fields.Char(
        help='This is a regex that is used for validation of the record '
             'value. Leave blank for no validation.',
    )
    supported_backend_ids = fields.Many2many(
        string='Supported Backends',
        comodel_name='dns.backend',
    )
    dns_bind_ids = fields.One2many(
        string='External Bindings',
        comodel_name='dns.record.type.bind',
        inverse_name='odoo_id',
    )

    @api.multi
    def name_get(self):
        return [
            (r.id, '%s - %s' % (r.code, r.name)) for r in self
        ]
