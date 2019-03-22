# -*- coding: utf-8 -*-
from odoo.addons.component.core import AbstractComponent


class DNSAbstractImportMapper(AbstractComponent):
    _name = 'dns.abstract.mapper'
    _inherit = 'base.import.mapper'
    _usage = 'import.mapper'
    _apply_on = ['dns.binding']
