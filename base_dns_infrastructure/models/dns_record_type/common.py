# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class DNSRecordType(models.Model):
    _name = "dns.record.type"
    _rec_name = "complete_name"
    _rec_names_search = ["name", "code"]
    _description = "DNS Record Type"

    name = fields.Char(
        string="DNS Type Name",
        required=True,
        help='Name of DNS record type, such a "A" or "CNAME".',
    )
    code = fields.Char(
        string="DNS Type Code",
        required=True,
    )
    active = fields.Boolean(default=True)
    help = fields.Text(
        help="Text that will be displayed to user as a formatting guide "
        "for this record type.",
    )
    validate_regex = fields.Text(
        help="This is a regex that is used for validation of the record "
        "value. Leave blank for no validation.",
    )

    complete_name = fields.Char(
        string="DNS Record Type Complete Name",
        compute="_compute_complete_name",
        recursive=True,
        store=True,
    )

    @api.depends("name", "code")
    def _compute_complete_name(self):
        for record_type in self:
            record_type.complete_name = "[%s]%s" % (
                record_type.code,
                record_type.name,
            )
