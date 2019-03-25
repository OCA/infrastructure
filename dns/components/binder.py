# -*- coding: utf-8 -*-
from odoo.addons.component.core import Component


class DNSBinder(Component):
    _name = 'dns.binder'
    _inherit = ['base.binder', 'base.dns.connector']
    _apply_on = ['dns.domain']
