# -*- coding: utf-8 -*-
# Copyright 2015 Elico Corp
# Copyright 2016 LasLabs Inc.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import fields, models
from openerp.addons.connector.connector import Binder
from ..backend import dns


@dns
class DNSModelBinder(Binder):
    """ Bindings are done directly on the binding model.

    Binding models are models called ``{normal_model}.bind``,
    like ``dns.record.bind`` or ``dns.zone.bind``.
    They are ``_inherits`` of the normal models and contains
    the DNS ID, the ID of the DNS Backend and the additional
    fields belonging to the DNS instance.
    """

    _model_name = [
        'dns.record.bind',
        'dns.zone.bind',
    ]

    # Name of Odoo field containing external record ID
    _external_field = 'dns_id_external'
    # Name of Odoo field containing backend record relation
    _backend_field = 'dns_backend_id'
    # Name of Odoo field on binding record, relating to regular record
    _openerp_field = 'odoo_id'
    # Name of Odoo field containing last successful sync date
    _sync_date_field = 'sync_date'
    # Name of Odoo field containing last failed sync date
    _fail_date_field = 'fail_date'
    # Name of field on external system indicating last change time
    _external_date_field = 'updated_at'

    def bind(self, external_id, binding_id):
        """ Create the link between an External ID and an Odoo ID
        :param external_id: external id to bind
        :param binding_id: Odoo ID to bind
        :type binding_id: int
        """
        try:
            super(DNSModelBinder, self).bind(external_id, binding_id)
        except AssertionError:
            if not isinstance(binding_id, models.BaseModel):
                binding_id = self.model.browse(binding_id)
            binding_id.with_context(connector_no_export=True).write({
                self._fail_date_field: fields.Datetime.now(),
            })

    def _external_date_method(self, field_value):
        """ It executes w/ _external_date_field to create a Datetime obj

        Default implementation assumes it is already a Datetime obj.

        Args:
            field_value (mixed): Value of _external_date_field from
                external system

        Return:
            datetime.datetime()
        """
        return field_value
