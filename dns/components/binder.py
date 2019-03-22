# -*- coding: utf-8 -*-
from odoo.addons.component.core import Component


class DNSBinder(Component):
    _name = 'dns.binder'
    _inherit = 'base.binder'
    _apply_on = 'dns.binding'
