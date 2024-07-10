# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    domain_zone_ids = fields.One2many(
        string="Domain Zones",
        comodel_name="dns.domain_zone",
        inverse_name="owner_partner_id",
    )
