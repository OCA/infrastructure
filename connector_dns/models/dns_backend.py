# -*- coding: utf-8 -*-
# Copyright 2015 Elico Corp
# Copyright 2016 LasLabs Inc.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import datetime

from openerp import models, fields, api, _
from openerp.exceptions import ValidationError

from openerp.addons.connector.session import ConnectorSession

from ..unit.import_synchronizer import (import_batch,
                                        import_record,
                                        )


class DNSBackend(models.Model):
    _name = 'dns.backend'
    _inherit = 'connector.backend'
    _backend_type = 'dns'

    login = fields.Char(
        string='Login',
        help="Provider's login.",
        required=True
    )
    password = fields.Char(
        string='Password',
        help="Provider's password.",
        required=True
    )
    uri = fields.Char(
        help='URI to Provider endpoint.',
    )
    version = fields.Selection(
        selection='_select_version',
        string='Service Provider',
        help='DNS service provider',
        required=True
    )
    company_id = fields.Many2one(
        string='Company',
        comodel_name='res.company',
        default=lambda s: s.env.user.company_id,
    )
    is_default = fields.Boolean(
        default=True,
        help='Check this if this is the default connector for the company.'
        ' All newly created records for this company will be synced to the'
        ' default system. Only records that originated from non-default'
        ' systems will be synced with them.',
    )
    active = fields.Boolean(
        default=True,
    )
    import_zones_from_date = fields.Datetime()
    import_records_from_date = fields.Datetime()

    @api.model
    def _select_version(self):
        """ It returns the available DNS backend versions """
        return [('none', 'None')]

    @api.multi
    @api.constrains('is_default', 'company_id')
    def _check_default_for_company(self):
        """ It raises ``ValidationError`` when multiple defaults selected """
        for rec_id in self:
            domain = [
                ('company_id', '=', rec_id.company_id.id),
                ('is_default', '=', True),
            ]
            if len(self.search(domain)) > 1:
                raise ValidationError(_(
                    'This company already has a default CarePoint connector.',
                ))

    @api.multi
    def name_get(self):
        res = []
        for backend in self:
            res.append((backend.id, '%s (%s)' % (backend.name, backend.login)))
        return res

    @api.multi
    def check_dns_structure(self):
        """ It provides a central method used in every data import

        It should support non-singleton Recordsets.
        """
        return True

    @api.multi
    def _import_all(self, model):
        """ It runs delayed import for found external records for model

        Args:
            model (str): Binding model to perform import for: ``aws.dns.zone``
        """
        session = self._get_session()
        self.check_dns_structure()
        for backend in self:
            import_batch.delay(session, model, backend.id)

    @api.multi
    def _import_from_date(self, model, from_date_field, chg_date_field=None):
        """ It imports updated external records and sets last sync time

        Args:
            model (str): Binding model to perform import for: ``aws.dns.zone``
            from_date_field (str): Name of field on backend containing time
                of last sync for type. Will update to import start time after
                completed.
            chg_date_field (str): Name of field on external record containing
                last update time. ``None`` or ``False`` to use
                ``binder._external_date_field``
        """
        session = self._get_session()
        if not chg_date_field:
            binder = session.binder_for(model)
            chg_date_field = binder._external_date_field
        import_start_time = datetime.now()
        self.check_dns_structure()
        for backend in self:
            filters = {chg_date_field: {'<=': import_start_time}}
            from_date = getattr(backend, from_date_field)
            if from_date:
                filters[chg_date_field]['>='] = fields.Datetime.from_string(
                    from_date
                )
            import_batch.delay(session, model, backend.id, filters=filters)
        self.write({
            from_date_field: fields.Datetime.to_string(import_start_time),
        })

    @api.model
    def resync_all(self, binding_model, backend_ids=None):
        """ It re-imports all bound records with their external systems.

        This method is particularly useful if the external system does not
        have a webhook to notify Odoo of updated records.

        Args:
            binding_model (str): Name of binding model to sync
            backend_ids (list): List of ids for Backend records that should
                 be used as search filter. ``None`` or ``False`` for all.
        """
        session = self._get_session()
        domain = []
        if backend_ids:
            if isinstance(backend_ids, models.BaseModel):
                backend_ids = backend_ids.ids
            domain.append(
                ('dns_backend_id', 'in', backend_ids),
            )
        for record_id in self.env[binding_model].search(domain):
            for binding_id in record_id.dns_bind_ids:
                import_record.delay(session,
                                    binding_model,
                                    binding_id.backend_id.id,
                                    binding_id.dns_id_external,
                                    force=True,
                                    )

    @api.multi
    def import_dns_zones(self):
        self._import_from_date('dns.zone.bind',
                               'import_zones_from_date')

    @api.multi
    def import_dns_records(self):
        self._import_from_date('dns.record.bind',
                               'import_records_from_date')

    @api.model
    def _get_session(self):
        """ It returns a ConnectorSession for the environment """
        return ConnectorSession(
            self.env.cr, self.env.uid, context=self.env.context
        )
