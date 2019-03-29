# © 2019 Elico Corp (https://www.elico-corp.com).
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
from odoo.addons.component.core import Component


class DNSBinder(Component):
    _name = 'dns.binder'
    _inherit = ['base.binder', 'base.dns.connector']
    _apply_on = ['dns.domain']
