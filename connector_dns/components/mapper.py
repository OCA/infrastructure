# © 2019 Elico Corp (https://www.elico-corp.com).
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
from odoo.addons.component.core import AbstractComponent


class DNSAbstractImportMapper(AbstractComponent):
    _name = 'dns.abstract.mapper'
    _inherit = ['base.dns.connector', 'base.import.mapper']
    _usage = 'import.mapper'
