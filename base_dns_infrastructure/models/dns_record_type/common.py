# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class DNSRecordType(models.Model):
    _name = "dns.record.type"
    _rec_name = "complete_name"
    _description = "DNS Record Type"

    name = fields.Char(
        required=True,
        help='Name of DNS record type, such a "A" or "CNAME".',
    )
    code = fields.Char(
        required=True,
    )
    help = fields.Text(
        help="Text that will be displayed to user as a formatting guide "
        "for this record type.",
    )
    validate_regex = fields.Char(
        help="This is a regex that is used for validation of the record "
        "value. Leave blank for no validation.",
    )

    complete_name = fields.Char(
        "Complete Name", compute="_compute_complete_name", recursive=True, store=True
    )

    @api.depends("name", "code")
    def _compute_complete_name(self):
        for type in self:
            type.complete_name = "[%s]%s" % (type.code, type.name)
