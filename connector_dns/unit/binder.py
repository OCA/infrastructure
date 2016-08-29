# -*- coding: utf-8 -*-
# Copyright 2015 Elico Corp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from datetime import datetime
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT
from openerp.addons.connector.connector import Binder
from ..backend import dns


@dns
class DNSModelBinder(Binder):
    """
    Bindings are done directly on the binding model.

    Binding models are models called ``dns.{normal_model}``,
    like ``dns.record`` or ``dns.domain``.
    They are ``_inherits`` of the normal models and contains
    the DNS ID, the ID of the DNS Backend and the additional
    fields belonging to the DNS instance.
    """
    _model_name = [
        'dns.record',
        'dns.domain'
    ]
    _external_field = 'dns_id'
    _backend_field = 'dns_backend_id'
    _openerp_field = 'openerp_id'
    _sync_date_field = 'sync_date'

    def to_openerp(self, external_id, unwrap=False):
        """ Give the OpenERP ID for an external ID

        :param external_id: external ID for which we want the OpenERP ID
        :param unwrap: if True, returns the openerp_id of the dns_xx record,
                       else return the id (binding id) of that record
        :return: a record ID, depending on the value of unwrap,
                 or None if the external_id is not mapped
        :rtype: int
        """
        binding_ids = self.session.search(
            self.model._name,
            [(self._external_field, '=', str(external_id)),
             (self._backend_field, '=', self.backend_record.id)])
        if not binding_ids:
            return None
        assert len(binding_ids) == 1, "Several records found: %s" % binding_ids
        binding_id = binding_ids[0]
        if unwrap:
            model_id = self.session.read(
                self.model._name, binding_id, [self._openerp_field]
            )
            assert model_id
            return model_id[self._openerp_field][0]
        else:
            return binding_id

    def to_backend(self, binding_id):
        """ Give the external ID for an OpenERP ID

        :param binding_id: OpenERP ID for which we want the external id
        :return: backend identifier of the record
        """
        dns_record = self.session.read(
            self.model._name, binding_id, [self._external_field]
        )
        assert dns_record
        return dns_record[self._external_field]

    def bind(self, external_id, binding_id):
        """ Create the link between an external ID and an OpenERP ID and
        update the last synchronization date.

        :param external_id: External ID to bind
        :param binding_id: OpenERP ID to bind
        :type binding_id: int
        """
        # avoid to trigger the export when we modify the `dns_id`
        model = self.model.with_context(connector_no_export=True)
        binding = model.browse(binding_id)
        now_fmt = datetime.now().strftime(DEFAULT_SERVER_DATETIME_FORMAT)
        if external_id:
            state = 'done'
        else:
            state = 'exception'
        binding.write({'dns_id': str(external_id),
                       'state': state,
                       'sync_date': now_fmt})
