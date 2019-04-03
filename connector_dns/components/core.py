# © 2019 Elico Corp (https://www.elico-corp.com).
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
from odoo.addons.component.core import AbstractComponent


class BaseDNSConnectorComponent(AbstractComponent):
    """ Base DNS Connector Component
    All components of this connector should inherit from it.
    """
    _name = 'base.dns.connector'
    _inherit = 'base.connector'
    _collection = 'dns.backend'
