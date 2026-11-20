# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ContractContract(models.Model):
    _inherit = "contract.contract"

    domain_zone_ids = fields.One2many(
        string="Domain Zones",
        comodel_name="dns.domain_zone",
        inverse_name="contract_id",
    )

    dns_record_ids = fields.One2many(
        string="Domain Records",
        comodel_name="dns.record",
        inverse_name="contract_id",
    )


    domain_zone_count = fields.Integer(compute="_compute_dns_stats") 
    dns_record_count = fields.Integer(compute="_compute_dns_stats") 
    
    def _compute_dns_stats(self):
        for con in self:
            con.domain_zone_count = len(con.domain_zone_ids)
            con.dns_record_count = len(con.dns_record_ids)