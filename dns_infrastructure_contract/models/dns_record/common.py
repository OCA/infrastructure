# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import re

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class DNSRecord(models.Model):
    _inherit = "dns.record"

    contract_id = fields.Many2one(
        string="Contract", comodel_name="contract.contract"
    )