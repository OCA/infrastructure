# -*- coding: utf-8 -*-
# Copyright 2015 Elico Corp
# Copyright 2016 LasLabs Inc.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import re

from openerp import models, fields, api, _
from openerp.exceptions import ValidationError


class DNSRecordBind(models.Model):
    _name = 'dns.record.bind'
    _description = 'DNS Record Binding'
    _inherit = 'dns.binding'
    _inherits = {'dns.record': 'odoo_id'}

    odoo_id = fields.Many2one(
        comodel_name='dns.record',
        string='DNS Record',
        required=True,
        ondelete='cascade',
    )


class DNSRecord(models.Model):
    _name = 'dns.record'
    _description = 'DNS Record'

    name = fields.Char(
        string='Sub domain',
        help='Host record, such as "www".',
        required=True,
    )
    zone_id = fields.Many2one(
        string="Zone",
        comodel_name='dns.zone',
        ondelete='cascade',
        required=True,
        help="Hosted zone that this record is applied to.",
    )
    type_id = fields.Many2one(
        string='Record Type',
        comodel_name='dns.record.type',
        required=True,
    )
    type_help = fields.Text(
        string='Record Help',
        related='type_id.help',
    )
    value = fields.Text(
        string='Value',
        help="Enter multiple values on separate lines. Enclose text in "
             "quotation marks.",
        required=True,
    )
    ttl = fields.Integer(
        string='TTL',
        default=600,
        help="Time to Live, in seconds. Scope: 1-604800",
        required=True,
    )
    dns_bind_ids = fields.One2many(
        string='External Bindings',
        comodel_name='dns.record.bind',
        inverse_name='odoo_id',
    )

    @api.multi
    @api.constrains('type_id', 'value')
    def _check_value(self):
        """ It should raise ValidationError on invalid values """
        for rec_id in self:
            if not rec_id.type_id.validate_regex:
                continue
            if not re.search(
                rec_id.type_id.validate_regex.replace('\\\\', '\\'),
                rec_id.value,
                flags=re.MULTILINE | re.IGNORECASE,
            ):
                raise ValidationError(
                    _('"%s" does not match validation rule for a "%s" record')
                    % (rec_id.value, rec_id.type_id.display_name)
                )
