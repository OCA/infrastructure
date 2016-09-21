# -*- coding: utf-8 -*-
# Copyright 2013 Camptocamp SA
# Copyright 2015 LasLabs Inc.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


""" Importers for DNS.

An import can be skipped if the last sync date is more recent than
the last update in DNS.

They should call the ``bind`` method if the binder even if the records
are already bound, to update the last sync date.
"""


import logging
from openerp import fields, _
from openerp.addons.connector.queue.job import job
from openerp.addons.connector.connector import ConnectorUnit
from openerp.addons.connector.unit.synchronizer import Importer
from ..backend import dns
from ..connector import get_environment, add_checkpoint


_logger = logging.getLogger(__name__)


def int_or_str(val):
    try:
        return int(val)
    except:
        return str(val)


class DNSImporter(Importer):
    """ Base importer for DNS """

    def __init__(self, connector_env):
        """
        :param connector_env: current environment (backend, session, ...)
        :type connector_env: :class:`connector.connector.ConnectorEnvironment`
        """
        super(DNSImporter, self).__init__(connector_env)
        self.dns_id = None
        self.dns_record = None

    def _get_dns_data(self):
        """ Return the raw DNS data for ``self.dns_id`` """
        _logger.debug('Getting CP data for %s', self.dns_id)
        return self.backend_adapter.read(self.dns_id)

    def _before_import(self):
        """ Hook called before the import, when we have the DNS
        data"""

    def _is_current(self, binding):
        """ Return True if the import should be skipped because
        it is already up to date in Odoo"""
        assert self.dns_record

        if not binding:
            return  # it does not exist so it should not be skipped

        binder = self.binder_for(self.model._name)

        dns_date = getattr(
            binding, binder._external_date_field, False,
        )
        if not dns_date:
            return  # No external update date, always import

        sync_date = getattr(
            binding, binder._sync_date_field, False,
        )
        if not sync_date:
            return  # No internal update date, always import

        # Convert fields to Datetime objs for comparison
        sync_date = fields.Datetime.from_string(sync_date)
        dns_date = getattr(binding, binder._external_date_field)(dns_date)

        # if the last synchronization date is greater than the last
        # update in dns, we skip the import.
        # Important: at the beginning of the exporters flows, we have to
        # check if the dns_date is more recent than the sync_date
        # and if so, schedule a new import. If we don't do that, we'll
        # miss changes done in DNS
        return dns_date < sync_date

    def _import_dependency(self, dns_id, binding_model,
                           importer_class=None, always=False):
        """ Import a dependency.
        The importer class is a class or subclass of
        :class:`DNSImporter`. A specific class can be defined.
        :param dns_id: id of the related binding to import
        :param binding_model: name of the binding model for the relation
        :type binding_model: str | unicode
        :param importer_cls: :class:`odoo.addons.connector.\
                                     connector.ConnectorUnit`
                             class or parent class to use for the export.
                             By default: DNSImporter
        :type importer_cls: :class:`odoo.addons.connector.\
                                    connector.MetaConnectorUnit`
        :param always: if True, the record is updated even if it already
                       exists, note that it is still skipped if it has
                       not been modified on DNS since the last
                       update. When False, it will import it only when
                       it does not yet exist.
        :type always: boolean
        """
        if not dns_id:
            return
        if importer_class is None:
            importer_class = DNSImporter
        binder = self.binder_for(binding_model)
        if always or binder.to_openerp(dns_id) is None:
            importer = self.unit_for(importer_class, model=binding_model)
            importer.run(dns_id)

    def _import_dependencies(self):
        """ Import the dependencies for the record
        Import of dependencies can be done manually or by calling
        :meth:`_import_dependency` for each dependency.
        """
        return

    def _map_data(self):
        """ Returns an instance of
        :py:class:`~odoo.addons.connector.unit.mapper.MapRecord`
        """
        return self.mapper.map_record(self.dns_record)

    def _validate_data(self, data):
        """ Check if the values to import are correct
        Pro-actively check before the ``_create`` or
        ``_update`` if some fields are missing or invalid.
        Raise `InvalidDataError`
        """
        return

    def _must_skip(self):
        """ Hook called right after we read the data from the backend.
        If the method returns a message giving a reason for the
        skipping, the import will be interrupted and the message
        recorded in the job (if the import is called directly by the
        job, not by dependencies).
        If it returns None, the import will continue normally.
        :returns: None | str | unicode
        """
        return

    def _get_binding(self):
        return self.binder.to_openerp(self.dns_id,
                                      unwrap=False,
                                      browse=True,
                                      )

    def _create_data(self, map_record, **kwargs):
        return map_record.values(for_create=True, **kwargs)

    def _create(self, data):
        """ Create the Odoo record """
        # special check on data before import
        self._validate_data(data)
        model = self.model.with_context(connector_no_export=True)
        binding = model.create(data)
        return binding

    def _update_data(self, map_record, **kwargs):
        return map_record.values(**kwargs)

    def _update(self, binding, data):
        """ Update an Odoo record """
        # special check on data before import
        self._validate_data(data)
        binding.with_context(connector_no_export=True).write(data)
        return

    def _after_import(self, binding):
        """ Hook called at the end of the import """
        return

    def run(self, dns_id, force=False):
        """ Run the synchronization
        :param dns_id: identifier of the record on DNS
        """
        self.dns_id = dns_id
        self.dns_record = self._get_dns_data()
        lock_name = 'import({}, {}, {}, {})'.format(
            self.backend_record._name,
            self.backend_record.id,
            self.model._name,
            dns_id,
        )
        # Keep a lock on this import until the transaction is committed
        self.advisory_lock_or_retry(lock_name)

        skip = self._must_skip()
        if skip:
            return skip

        binding = self._get_binding()

        if not force and self._is_current(binding):
            return _('Already Up To Date.')
        self._before_import()

        # import the missing linked resources
        self._import_dependencies()

        map_record = self._map_data()

        if binding:
            record = self._update_data(map_record)
            self._update(binding, record)
        else:
            record = self._create_data(map_record)
            binding = self._create(record)

        self.binder.bind(self.dns_id, binding)

        self._after_import(binding)


class BatchImporter(Importer):
    """ The role of a BatchImporter is to search for a list of
    items to import, then it can either import them directly or delay
    the import of each item separately.
    """

    def run(self, filters=None):
        """ Run the synchronization """
        if filters is None:
            filters = {}
        record_ids = self.backend_adapter.search(**filters)
        for record_id in record_ids:
            self._import_record(record_id)

    def _import_record(self, record_id):
        """ Import a record directly or delay the import of the record.
        Method to be implemented in sub-classes.
        """
        raise NotImplementedError


class DirectBatchImporter(BatchImporter):
    """ Import the records directly, without delaying the jobs. """
    _model_name = None

    def _import_record(self, record_id):
        """ Import the record directly """
        import_record(self.session,
                      self.model._name,
                      self.backend_record.id,
                      int_or_str(record_id))


class DelayedBatchImporter(BatchImporter):
    """ Delay import of the records """
    _model_name = None

    def _import_record(self, record_id, **kwargs):
        """ Delay the import of the records"""
        import_record.delay(self.session,
                            self.model._name,
                            self.backend_record.id,
                            int_or_str(record_id),
                            **kwargs)


@dns
class AddCheckpoint(ConnectorUnit):
    """ Add a connector.checkpoint on the underlying model
    (not the dns.* but the _inherits'ed model) """

    _model_name = ['dns.product.product',
                   'dns.product.category',
                   ]

    def run(self, odoo_binding_id):
        binding = self.model.browse(odoo_binding_id)
        record = binding.odoo_id
        add_checkpoint(self.session,
                       record._model._name,
                       record.id,
                       self.backend_record.id)


@job(default_channel='root.dns')
def import_batch(session, model_name, backend_id, filters=None):
    """ Prepare a batch import of records from DNS """
    env = get_environment(session, model_name, backend_id)
    importer = env.get_connector_unit(BatchImporter)
    importer.run(filters=filters)


@job(default_channel='root.dns')
def import_record(session, model_name, backend_id, dns_id, force=False):
    """ Import a record from DNS """
    env = get_environment(session, model_name, backend_id)
    importer = env.get_connector_unit(DNSImporter)
    importer.run(dns_id, force=force)
