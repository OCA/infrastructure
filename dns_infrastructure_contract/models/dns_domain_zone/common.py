# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo import fields, models


class DNSDomainZone(models.Model):
    _inherit = "dns.domain_zone"

    contract_id = fields.Many2one(string="Contract", comodel_name="contract.contract")
