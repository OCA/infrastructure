# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from validator_collection import checkers

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class DNSDomainZone(models.Model):
    _name = "dns.domain_zone"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _parent_store = True
    _rec_name = "complete_name"
    _order = "complete_name"
    _description = "DNS Domain Zone"

    name = fields.Char(
        string="Domain Name",
        required=True,
        help="""
        In case of a domain FQDN Hosted domain zone name, such as amazon.com
        In case of a sub domain, the first key of the sub domain
        """,
    )
    active = fields.Boolean(default=True)
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("production", "Production"),
            ("exception", "Exception"),
            ("inactive", "Inactive"),
        ],
        default="draft",
        help="In Production when active otherwise Exception",
        tracking=True,
    )

    owner_partner_id = fields.Many2one(string="Owner", comodel_name="res.partner")
    renew_date = fields.Date(string="Renewal Date", tracking=True)

    record_ids = fields.One2many(
        string="DNS Records",
        comodel_name="dns.record",
        inverse_name="zone_id",
    )

    parent_id = fields.Many2one(
        comodel_name="dns.domain_zone",
        string="Parent Domain",
        index=True,
        ondelete="restrict",
        tracking=True,
    )
    parent_path = fields.Char(index=True, unaccent=False)

    complete_name = fields.Char(
        string="Complete Domain Name",
        compute="_compute_complete_name",
        recursive=True,
        store=True,
    )

    @api.constrains("complete_name")
    def _check_valid_domain_name(self):
        for record in self:
            valid = checkers.is_domain(
                record.complete_name,
            )
            if not valid:
                raise ValidationError(
                    _('"%s" is not a valid FQDN') % (record.complete_name,)
                )

    @api.depends("name", "parent_id")
    def _compute_complete_name(self):
        for record in self:
            if record.parent_id:
                record.complete_name = "%s.%s" % (
                    record.name,
                    record.parent_id.complete_name,
                )
            else:
                record.complete_name = record.name
