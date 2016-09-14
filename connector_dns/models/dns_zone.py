# -*- coding: utf-8 -*-
# Copyright 2015 Elico Corp
# Copyright 2016 LasLabs Inc.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, fields


class DNSZoneBind(models.Model):
    _name = 'dns.zone.bind'
    _description = 'DNS Zone Binding'
    _inherit = 'dns.binding'
    _inherits = {'dns.zone': 'odoo_id'}

    odoo_id = fields.Many2one(
        comodel_name='dns.zone',
        string='DNS Zone',
        required=True,
        ondelete='cascade',
    )


class DNSZone(models.Model):
    _name = 'dns.zone'

    name = fields.Char(
        string='Name',
        required=True,
        help='Hosted zone name, such as "amazon.com".',
    )
    record_ids = fields.One2many(
        string='DNS Records',
        comodel_name='dns.record',
        inverse_name='zone_id',
    )
    dns_bind_ids = fields.One2many(
        string='External Bindings',
        comodel_name='dns.zone.bind',
        inverse_name='odoo_id',
    )
