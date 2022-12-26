# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import re

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class DNSRecord(models.Model):
    _name = "dns.record"
    _description = "DNS Record"

    name = fields.Char(
        string="Sub domain",
        help='Host record, such as "www".',
        required=True,
    )
    zone_id = fields.Many2one(
        string="Zone",
        comodel_name="dns.domain_zone",
        ondelete="cascade",
        required=True,
        help="Hosted zone that this record is applied to.",
    )
    type_id = fields.Many2one(
        string="Record Type",
        comodel_name="dns.record.type",
        required=True,
    )
    type_help = fields.Text(
        string="Record Help",
        related="type_id.help",
    )
    value = fields.Char(
        string="Value",
        help="Enter multiple values on separate lines. Enclose text in "
        "quotation marks.",
        required=True,
    )
    ttl = fields.Integer(
        string="TTL",
        default=600,
        help="Time to Live, in seconds. Scope: 1-604800",
        required=True,
    )

    @api.constrains("type_id", "value")
    def _check_value(self):
        """It should raise ValidationError on invalid values"""
        for rec_id in self:
            if not rec_id.type_id.validate_regex:
                continue
            if not re.search(
                rec_id.type_id.validate_regex.replace("\\\\", "\\"),
                rec_id.value,
                flags=re.MULTILINE | re.IGNORECASE,
            ):
                raise ValidationError(
                    _('"%s" does not match validation rule for a "%s" record')
                    % (rec_id.value, rec_id.type_id.display_name)
                )
