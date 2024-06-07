# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import re

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class DNSRecord(models.Model):
    _name = "dns.record"
    _rec_name = "complete_name"
    _order = "complete_name"
    _description = "DNS Record"

    complete_name = fields.Char(
        string="DNS Record Name",
        compute="_compute_complete_name",
        recursive=True,
        store=True,
    )
    active = fields.Boolean(default=True)
    zone_id = fields.Many2one(
        string="Domain",
        comodel_name="dns.domain_zone",
        ondelete="restrict",
        required=True,
        help="Domain that this record is applied to.",
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
        string="DNS Record Value",
        help="Enter multiple values on separate lines. Enclose text in "
        "quotation marks.",
        required=True,
    )
    ttl = fields.Integer(
        default=60,
        help="Time to Live, in seconds. Scope: 1-604800",
        required=True,
        string="TTL",
    )

    @api.depends(
        "zone_id.complete_name",
        "type_id.code",
    )
    def _compute_complete_name(self):
        for record in self:
            record.complete_name = "%s [%s]: %s" % (
                record.zone_id.complete_name,
                record.type_id.code,
                record.value,
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
                    _(
                        "%(value)s does not match validation rule for a %(type)s record",
                        value=rec_id.value,
                        type=rec_id.type_id.display_name,
                    )
                )
