# -*- coding: utf-8 -*-
# Copyright 2015 Elico Corp
# Copyright 2016 LasLabs Inc.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, fields, api
from openerp.addons.connector.connector import Environment
from openerp.addons.connector.checkpoint import checkpoint


def get_environment(session, model_name, backend_id):
    """ Create an environment to work with.  """
    backend_record = session.env['dns.backend'].browse(backend_id)
    env = Environment(backend_record, session, model_name)
    return env


class DNSBinding(models.AbstractModel):
    """ Abstract Model for the Bindigs.
    All the models used as bindings between External System and Odoo
    (``aws.dns.record``, ``aws.dns.zone``, ...) should ``_inherit`` it.
    """
    _name = 'dns.binding'
    _inherit = 'external.binding'
    _description = 'DNS Binding (abstract)'

    dns_backend_id = fields.Many2one(
        comodel_name='dns.backend',
        string='DNS Backend',
        store=True,
        required=True,
        ondelete='restrict',
        default=lambda s: s._default_dns_backend_id()
    )
    dns_id_external = fields.Char(
        string='External ID',
        help='ID of the record in external system.',
    )
    fail_date = fields.Datetime()

    _sql_constraints = [
        ('backend_uniq', 'unique(dns_backend_id, dns_id_external)',
         'A binding already exists with the same DNS External ID.'),
    ]

    @api.model
    def _default_dns_backend_id(self):
        return self.env['dns.backend'].search([
            ('is_default', '=', True),
            ('active', '=', True),
        ],
            limit=1,
        )


def add_checkpoint(session, model_name, record_id, backend_id):
    """ Add a row in the model ``connector.checkpoint`` for a record,
    meaning it has to be reviewed by a user.
    :param session: current session
    :type session: :class:`openerp.addons.connector.session.ConnectorSession`
    :param model_name: name of the model of the record to be reviewed
    :type model_name: str
    :param record_id: ID of the record to be reviewed
    :type record_id: int
    :param backend_id: ID of the dnspod Backend
    :type backend_id: int
    """
    return checkpoint.add_checkpoint(session, model_name, record_id,
                                     'dns.backend', backend_id)
