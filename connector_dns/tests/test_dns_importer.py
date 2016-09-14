# -*- coding: utf-8 -*-
# Copyright 2016 LasLabs Inc.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import mock
from contextlib import contextmanager

from openerp import fields, _

from openerp.addons.connector_dns.unit import import_synchronizer

from .common import SetUpDNSBase

model = 'openerp.addons.connector_dns.unit.import_synchronizer'


class TestDNSImporter(SetUpDNSBase):

    def setUp(self):
        super(TestDNSImporter, self).setUp()
        self.model = 'dns.zone.bind'
        self.dns_id = 'dns_id'
        self.dns_record = {
            'updated_at': fields.Datetime.from_string('2016-05-10 00:00:00'),
        }
        self.binding_id = 1234
        self.Importer = import_synchronizer.DNSImporter
        self.mock_env = self.get_dns_helper(
            self.model
        )

    @contextmanager
    def mock_base_importer(self, obj, patches=None, add=True):
        """ Inject mock as only parent to DNSExporter
        Normal method of injection would not work due to super raising
        ``TypeError: must be type, not MagicMock``
        """
        _patches = [
            'binder_for',
            'unit_for',
            '_validate_data',
            'advisory_lock_or_retry',
            '_must_skip',
            '_before_import',
            '_get_dns_data',
        ]
        if patches:
            if add:
                patches = _patches + patches
        else:
            patches = _patches
        patches = {p: mock.DEFAULT for p in patches}
        with mock.patch.multiple(obj, **patches) as mk:
            if mk.get('binder_for'):
                mk['binder_for'].return_value = self.get_mock_binder()
            yield mk

    def _new_record(self, sync_date='2016-01-01 00:00:00'):
        return self.env[self.model].create({
            'name': 'Test',
            'sync_date': sync_date,
        })

    def _new_importer(self, dns_id=None, dns_record=None):
        importer = self.Importer(self.mock_env)
        if dns_id is not None:
            importer.dns_id = dns_id
        if dns_record is not None:
            importer.dns_record = dns_record
        return importer

    def test_int_or_str_int(self):
        """ It should return an int when parseable as such """
        expect = 12345
        res = import_synchronizer.int_or_str(str(expect))
        self.assertEqual(expect, res)

    def test_int_or_str_str(self):
        """ It should return a string when not parseable as int """
        expect = mock
        res = import_synchronizer.int_or_str(expect)
        self.assertEqual(str(expect), res)

    def test_init_calls_sets_dns_id(self):
        """ It should blank dns_id on init """
        res = self._new_importer()
        self.assertEqual(None, res.dns_id)

    def test_init_calls_sets_dns_record(self):
        """ It should blank dns_record on init """
        res = self._new_importer()
        self.assertEqual(None, res.dns_record)

    def test_get_dns_data_read(self):
        """ It should call read on adapter for dns id """
        importer = self._new_importer(self.dns_id)
        with self.mock_adapter(importer) as mk:
            importer._get_dns_data()
            mk.read.assert_called_once_with(self.dns_id)

    def test_get_dns_data_return(self):
        """ It should return result of adapter read op """
        importer = self._new_importer(self.dns_id)
        with self.mock_adapter(importer) as mk:
            res = importer._get_dns_data()
            self.assertEqual(mk.read(), res)

    def test_is_current_assert_record(self):
        """ It should assert that a dns_record is set """
        with self.assertRaises(AssertionError):
            self._new_importer()._is_current(None)

    def test_is_current_no_updated_at(self):
        """ It should return None when no updated_at present on record """
        importer = self._new_importer(dns_record={'updated_at': False})
        with self.mock_base_importer(importer):
            res = importer._is_current(True)
            self.assertEqual(None, res)

    def test_is_current_no_binding(self):
        """ It should return None when no binding was provided """
        res = self._new_importer(dns_record=self.dns_record)
        res = res._is_current(False)
        self.assertEqual(None, res)

    def test_is_current_no_sync_date(self):
        """ It should return None when no sync_date in binding """
        rec_id = self._new_record(None)
        importer = self._new_importer(dns_record=self.dns_record)
        with self.mock_base_importer(importer):
            res = importer._is_current(rec_id)
            self.assertEqual(None, res)

    def test_is_current_should_not_sync(self):
        """ It should return False when DNS is newer than Binding """
        rec_id = self._new_record()
        importer = self._new_importer(dns_record=self.dns_record)
        with self.mock_base_importer(importer):
            res = importer._is_current(rec_id)
            self.assertFalse(res)

    def test_import_dependency_no_dns_id(self):
        """ It should return None when no dns_id supplied """
        res = self._new_importer()._import_dependency(False, True)
        self.assertEqual(None, res)

    def test_import_dependency_gets_binder(self):
        """ It should get binder for binding_model """
        importer = self._new_importer()
        with self.mock_base_importer(importer):
            importer.binder_for.side_effect = self.EndTestException
            with self.assertRaises(self.EndTestException):
                importer._import_dependency(True, self.model)
            importer.binder_for.assert_called_once_with(
                self.model,
            )

    def test_import_dependency_always(self):
        """ It should always proceed to import if always is True """
        importer = self._new_importer()
        with self.mock_base_importer(importer):
            importer.unit_for.side_effect = self.EndTestException
            with self.assertRaises(self.EndTestException):
                importer._import_dependency(
                    True, self.model, always=True
                )
            importer.binder_for.to_openerp.assert_not_called()

    def test_import_dependency_no_odoo_binder(self):
        """ It should attempt to get odoo for binder if not always """
        importer = self._new_importer()
        with self.mock_base_importer(importer):
            importer._import_dependency(
                self.dns_id, self.model,
            )
            importer.binder_for().to_openerp.assert_called_once_with(
                self.dns_id
            )

    def test_import_dependency_gets_unit_default(self):
        """ It should get proper importer unit w/ default Importer """
        importer = self._new_importer()
        with self.mock_base_importer(importer):
            importer.unit_for.side_effect = self.EndTestException
            with self.assertRaises(self.EndTestException):
                importer._import_dependency(
                    True, self.model, always=True
                )
            importer.unit_for.assert_called_once_with(
                self.Importer, model=self.model,
            )

    def test_import_dependency_gets_unit_defined(self):
        """ It should get proper importer unit w/ defined Importer """
        expect = mock.MagicMock()
        importer = self._new_importer()
        with self.mock_base_importer(importer):
            importer.unit_for.side_effect = self.EndTestException
            with self.assertRaises(self.EndTestException):
                importer._import_dependency(
                    True, self.model, importer_class=expect, always=True
                )
            importer.unit_for.assert_called_once_with(
                expect, model=self.model,
            )

    def test_import_dependency_runs_import(self):
        """ It should run importer w/ proper args """
        importer = self._new_importer()
        with self.mock_base_importer(importer):
            importer._import_dependency(
                self.dns_id, self.model, always=True
            )
            importer.unit_for().run.assert_called_once_with(
                self.dns_id
            )

    def test_import_dependencies_none(self):
        """ It should return None on base class """
        res = self._new_importer()._import_dependencies()
        self.assertEqual(None, res)

    def test_map_data_call(self):
        """ It should get map record w/ proper args """
        importer = self._new_importer(dns_record=self.dns_record)
        with self.mock_base_importer(importer, ['_mapper']):
            importer._map_data()
            importer.mapper.map_record.assert_called_once_with(
                self.dns_record
            )

    def test_map_data_return(self):
        """ It should return data mapper """
        importer = self._new_importer(dns_record=self.dns_record)
        with self.mock_base_importer(importer, ['_mapper']):
            res = importer._map_data()
            self.assertEqual(importer.mapper.map_record(), res)

    def test_validate_data_none(self):
        """ It should return None on base class """
        res = self._new_importer()._validate_data(True)
        self.assertEqual(None, res)

    def test_must_skip_none(self):
        """ It should return None on base class """
        res = self._new_importer()._must_skip()
        self.assertEqual(None, res)

    def test_get_binding_call(self):
        """ It should get binding w/ proper args """
        importer = self._new_importer(self.dns_id)
        with self.mock_base_importer(importer):
            importer._get_binding()
            importer.binder.to_openerp.assert_called_once_with(
                self.dns_id, unwrap=False, browse=True,
            )

    def test_get_binding_return(self):
        """ It should return resulting binding """
        importer = self._new_importer(self.dns_id)
        with self.mock_base_importer(importer):
            res = importer._get_binding()
            self.assertEqual(importer.binder.to_openerp(), res)

    def test_create_data_call(self):
        """ It should inject proper vals into map record """
        map_record = mock.MagicMock()
        expect = {'test': 123, 'test2': 456}
        self._new_importer(self.dns_id)._create_data(
            map_record, **expect
        )
        map_record.values.assert_called_once_with(
            for_create=True, **expect
        )

    def test_create_data_return(self):
        """ It should inject proper vals into map record """
        map_record = mock.MagicMock()
        res = self._new_importer(self.dns_id)._create_data(map_record)
        self.assertEqual(map_record.values(), res)

    def test_create_validates_data(self):
        """ It should validate data """
        expect = 'expect'
        importer = self._new_importer()
        with self.mock_base_importer(importer):
            importer._validate_data.side_effect = self.EndTestException
            with self.assertRaises(self.EndTestException):
                importer._create(expect)
            importer._validate_data.assert_called_once_with(expect)

    def test_create_gets_model_with_context(self):
        """ It should get model with context to avoid infinite loop """
        importer = self._new_importer()
        with self.mock_base_importer(importer, ['connector_env']):
            importer.connector_env.model.with_context.side_effect = \
                self.EndTestException
            with self.assertRaises(self.EndTestException):
                importer._create(None)
            importer.connector_env.model.with_context.assert_called_once_with(
                connector_no_export=True,
            )

    def test_create_does_create(self):
        """ It should create binding w/ data """
        expect = 'expect'
        importer = self._new_importer()
        with self.mock_base_importer(importer, ['connector_env']):
            mk = importer.connector_env.model.with_context
            mk().create.side_effect = self.EndTestException
            with self.assertRaises(self.EndTestException):
                importer._create(expect)
            mk().create.assert_called_once_with(expect)

    def test_create_returns_binding(self):
        """ It should return new binding """
        importer = self._new_importer()
        with self.mock_base_importer(importer, ['connector_env']):
            res = importer._create(None)
            self.assertEqual(
                importer.connector_env.model.with_context().create(), res
            )

    def test_update_data_call(self):
        """ It should inject proper vals into map record """
        map_record = mock.MagicMock()
        expect = {'test': 123, 'test2': 456}
        self._new_importer(self.dns_id)._update_data(
            map_record, **expect
        )
        map_record.values.assert_called_once_with(**expect)

    def test_update_data_return(self):
        """ It should inject proper vals into map record """
        map_record = mock.MagicMock()
        res = self._new_importer(self.dns_id)._update_data(map_record)
        self.assertEqual(map_record.values(), res)

    def test_update_gets_binding_with_context(self):
        """ It should get model with context to avoid infinite loop """
        expect = 'expect'
        mk = mock.MagicMock()
        importer = self._new_importer()
        with self.mock_base_importer(importer):
            mk.with_context.side_effect = self.EndTestException
            with self.assertRaises(self.EndTestException):
                importer._update(mk, expect)
            mk.with_context.assert_called_once_with(
                connector_no_export=True,
            )

    def test_update_does_write(self):
        """ It should update binding w/ data """
        expect = 'expect'
        mk = mock.MagicMock()
        importer = self._new_importer()
        with self.mock_base_importer(importer):
            mk.with_context().write.side_effect = self.EndTestException
            with self.assertRaises(self.EndTestException):
                importer._update(mk, expect)
            mk.with_context().write.assert_called_once_with(expect)

    def test_after_import_none(self):
        """ It should return None on base class """
        res = self._new_importer()._after_import(None)
        self.assertEqual(None, res)

    def test_run_sets_dns_id(self):
        """ It should set dns_id on importer """
        importer = self._new_importer()
        with self.mock_base_importer(importer):
            importer._get_dns_data.side_effect = self.EndTestException
            with self.assertRaises(self.EndTestException):
                importer.run(self.dns_id)
            self.assertEqual(self.dns_id, importer.dns_id)

    def test_run_returns_skip_if_skip(self):
        """ It should return skip if skip """
        expect = 'expect'
        importer = self._new_importer()
        with self.mock_base_importer(importer):
            importer._must_skip.return_value = expect
            res = importer.run(self.dns_id)
            self.assertEqual(expect, res)

    def test_run_gets_binding(self):
        """ It should get binding """
        importer = self._new_importer()
        with self.mock_base_importer(importer, ['_get_binding']):
            importer._must_skip.return_value = False
            importer._get_binding.side_effect = self.EndTestException
            with self.assertRaises(self.EndTestException):
                importer.run(self.dns_id)

    def test_run_does_force(self):
        """ It should not see if binding is current if forced """
        importer = self._new_importer()
        with self.mock_base_importer(
            importer, ['_before_import', '_is_current']
        ):
            importer._must_skip.return_value = False
            importer._before_import.side_effect = self.EndTestException
            with self.assertRaises(self.EndTestException):
                importer.run(self.dns_id, True)
            importer._is_current.assert_not_called()

    def test_run_no_force(self):
        """ It should return translated up to date if current """
        importer = self._new_importer()
        with self.mock_base_importer(importer, ['_is_current']):
            importer._must_skip.return_value = False
            importer._is_current.return_value = True
            res = importer.run(self.dns_id)
            self.assertEqual(
                _('Already Up To Date.'), res,
            )

    def test_run_import_depends(self):
        """ It should import dependencies first """
        importer = self._new_importer()
        with self.mock_base_importer(importer, ['_import_dependencies']):
            importer._must_skip.return_value = False
            importer._import_dependencies.side_effect = self.EndTestException
            with self.assertRaises(self.EndTestException):
                importer.run(self.dns_id, True)

    def test_run_gets_map_record(self):
        """ It should get the map record """
        importer = self._new_importer()
        with self.mock_base_importer(importer, ['_map_data']):
            importer._map_data.side_effect = self.EndTestException
            importer._must_skip.return_value = False
            with self.assertRaises(self.EndTestException):
                importer.run(self.dns_id, True)

    def test_run_update_data(self):
        """ It should call update_data w/ map_record if existing """
        importer = self._new_importer()
        with self.mock_base_importer(importer, ['_map_data',
                                                '_get_binding',
                                                '_update_data',
                                                ]):
            importer._get_binding.return_value = True
            importer._update_data.side_effect = self.EndTestException
            importer._must_skip.return_value = False
            with self.assertRaises(self.EndTestException):
                importer.run(self.dns_id, True)
            importer._update_data.assert_called_once_with(
                importer._map_data(),
            )

    def test_run_update(self):
        """ It should call update w/ binding and record """
        importer = self._new_importer()
        with self.mock_base_importer(importer, ['_map_data',
                                                '_get_binding',
                                                '_update_data',
                                                '_update',
                                                ]):
            importer._get_binding.return_value = True
            importer._update.side_effect = self.EndTestException
            importer._must_skip.return_value = False
            with self.assertRaises(self.EndTestException):
                importer.run(self.dns_id, True)
            importer._update.assert_called_once_with(
                importer._get_binding(), importer._update_data(),
            )

    def test_run_create_data(self):
        """ It should call update_data w/ map_record if not existing """
        importer = self._new_importer()
        with self.mock_base_importer(importer, ['_map_data',
                                                '_get_binding',
                                                '_create_data',
                                                ]):
            importer._get_binding.return_value = False
            importer._create_data.side_effect = self.EndTestException
            importer._must_skip.return_value = False
            with self.assertRaises(self.EndTestException):
                importer.run(self.dns_id, True)
            importer._create_data.assert_called_once_with(
                importer._map_data(),
            )

    def test_run_create(self):
        """ It should call create w/ record """
        importer = self._new_importer()
        with self.mock_base_importer(importer, ['_map_data',
                                                '_get_binding',
                                                '_create_data',
                                                '_create',
                                                ]):
            importer._get_binding.return_value = False
            importer._create.side_effect = self.EndTestException
            importer._must_skip.return_value = False
            with self.assertRaises(self.EndTestException):
                importer.run(self.dns_id, True)
            importer._create.assert_called_once_with(
                importer._create_data(),
            )
