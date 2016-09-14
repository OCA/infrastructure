# -*- coding: utf-8 -*-
# Copyright 2016 LasLabs Inc.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import mock
import psycopg2
from contextlib import contextmanager

from openerp import _

from openerp.addons.connector_dns.unit import export_synchronizer

from .common import SetUpDNSBase

model = 'openerp.addons.connector_dns.unit.export_synchronizer'


@contextmanager
def mock_retryable_job_error():
    with mock.patch('%s.RetryableJobError' % model) as mk:
        yield mk


class UniqueViolationException(psycopg2.IntegrityError):
    def __init__(self, pgcode=psycopg2.errorcodes.UNIQUE_VIOLATION):
        self.pgcode = pgcode


class TestDNSExporter(SetUpDNSBase):

    def setUp(self):
        super(TestDNSExporter, self).setUp()
        self.model = 'dns.zone.bind'
        self.binding_id = 1234
        self.Exporter = export_synchronizer.DNSExporter

    @contextmanager
    def mock_base_exporter(self, obj, patches=None, add=True):
        """ Inject mock as only parent to DNSExporter
        Normal method of injection would not work due to super raising
        ``TypeError: must be type, not MagicMock``
        """
        _patches = [
            'binder_for',
            'unit_for',
            'session',
            '_mapper',
        ]
        if patches:
            if add:
                patches = _patches + patches
        else:
            patches = _patches
        patches = {p: mock.DEFAULT for p in patches}
        with mock.patch.multiple(obj, **patches) as mk:
            if mk.get('binder_for'):
                mk['binder_for'] = self.get_mock_binder()
            yield mk

    def _new_exporter(self, dns_id=None, binding_record=None,
                      binding_id=None,
                      ):
        self.mock_env = self.get_dns_helper(
            self.model
        )
        exporter = self.Exporter(self.mock_env)
        exporter.dns_id = dns_id
        exporter.binding_record = binding_record
        exporter.binding_id = binding_id
        return exporter

    def _new_record(self):
        return self.env[self.model].create({
            'name': 'Test',
        })

    def test_lock_sql(self):
        """ It should attempt proper SQL execution """
        exporter = self._new_exporter(binding_id=self.binding_id)
        with self.mock_base_exporter(exporter):
            exporter.session.cr.execute.side_effect = self.EndTestException
            with self.assertRaises(self.EndTestException):
                exporter._lock()
            exporter.session.cr.execute.assert_called_once_with(
                "SELECT id FROM %s WHERE ID = %%s FOR UPDATE NOWAIT" % (
                    self.model.replace('.', '_'),
                ),
                (self.binding_id, ),
                log_exceptions=False,
            )

    # def test_lock_retryable(self):
    #     """ It should attempt proper SQL execution """
    #     exporter = self._new_exporter()
    #     with self.mock_base_exporter(exporter):
    #         with mock_retryable_job_error() as err:
    #             exporter.session.cr.execute.side_effect = \
    #                 psycopg2.OperationalError
    #             with self.assertRaises(err):
    #                 exporter._lock()

    def test_has_to_skip(self):
        """ It should return False """
        exporter = self._new_exporter()
        with self.mock_base_exporter(exporter):
            res = exporter._has_to_skip()
            self.assertFalse(res)

    def test_export_dependency_no_relation(self):
        """ It should return None when no relation """
        exporter = self._new_exporter()
        with self.mock_base_exporter(exporter):
            res = exporter._export_dependency(None, None)
            self.assertEqual(None, res)

    def test_export_dependency_gets_binder(self):
        """ It should get binder for model """
        expect = self._new_record()
        exporter = self._new_exporter()
        with self.mock_base_exporter(exporter):
            exporter.binder_for.side_effect = self.EndTestException
            with self.assertRaises(self.EndTestException):
                exporter._export_dependency(expect, self.model)
            exporter.binder_for.assert_called_once_with(self.model)

    def test_export_dependency_wrap_search(self):
        """ It should perform query for binding record when wrapped """
        rec_id = self._new_record()
        expect = rec_id.odoo_id
        exporter = self._new_exporter()
        with self.mock_base_exporter(exporter):
            with mock.patch.object(exporter.session, 'env'):
                search = exporter.env[self.model].search
                search.side_effect = self.EndTestException
                with self.assertRaises(self.EndTestException):
                    exporter._export_dependency(expect, self.model)
                search.assert_called_once_with([
                    (exporter.binder_for()._openerp_field, '=', expect.id),
                    (exporter.binder_for()._backend_field,
                     '=', exporter.backend_record.id),
                ])

    def test_export_dependency_wrap_multiple_results(self):
        """ It should assert max of one binding result """
        expect = self._new_record().odoo_id
        exporter = self._new_exporter()
        with self.mock_base_exporter(exporter):
            with mock.patch.object(exporter.session, 'env'):
                search = exporter.env[self.model].search
                search.return_value = [1, 2]
                with self.assertRaises(AssertionError):
                    exporter._export_dependency(expect, self.model)

    def test_export_dependency_unwrapped(self):
        """ It should call to_backend with proper args from unwrapped """
        expect = self._new_record()
        exporter = self._new_exporter()
        with self.mock_base_exporter(exporter):
            to_backend = exporter.binder_for().to_backend
            to_backend.side_effect = self.EndTestException
            with self.assertRaises(self.EndTestException):
                exporter._export_dependency(expect, self.model)
            to_backend.assert_called_once_with(
                expect,
                wrap=False
            )

    def test_export_dependency_run_no_force(self):
        """ It should not trigger export when not forced and existing """
        expect = self._new_record()
        exporter = self._new_exporter()
        with self.mock_base_exporter(exporter):
            to_backend = exporter.binder_for().to_backend
            to_backend.return_value = True
            exporter._export_dependency(expect, self.model, force=False)
            exporter.unit_for().run.assert_not_called()

    def test_export_dependency_run_force(self):
        """ It should trigger export when forced and existing """
        expect = self._new_record()
        exporter = self._new_exporter()
        with self.mock_base_exporter(exporter):
            to_backend = exporter.binder_for().to_backend
            to_backend.return_value = True
            exporter._export_dependency(expect, self.model, force=True)
            exporter.unit_for().run.assert_called_once_with(expect.id)

    def test_export_dependency_run_no_exist(self):
        """ It should trigger export when not forced and not existing """
        expect = self._new_record()
        exporter = self._new_exporter()
        with self.mock_base_exporter(exporter):
            to_backend = exporter.binder_for().to_backend
            to_backend.return_value = False
            exporter._export_dependency(expect, self.model, force=False)
            exporter.unit_for().run.assert_called_once_with(expect.id)

    def test_export_dependencies(self):
        """ It should return None """
        res = self._new_exporter()._export_dependencies()
        self.assertEqual(None, res)

    def test_map_data_call(self):
        """ It should get map record for binding record """
        exporter = self._new_exporter()
        with self.mock_base_exporter(exporter):
            exporter._map_data()
            exporter.mapper.map_record.assert_called_once_with(
                exporter.binding_record
            )

    def test_map_data_return(self):
        """ It should return map record for binding record """
        exporter = self._new_exporter()
        with self.mock_base_exporter(exporter):
            res = exporter._map_data()
            self.assertEqual(exporter.mapper.map_record(), res)

    def test_validate_create_data(self):
        """ It should return None """
        res = self._new_exporter()._validate_create_data(True)
        self.assertEqual(None, res)

    def test_validate_update_data(self):
        """ It should return None """
        res = self._new_exporter()._validate_update_data(True)
        self.assertEqual(None, res)

    def test_create_data_call(self):
        """ It should inject proper vals into map record """
        map_record = mock.MagicMock()
        expect = {'test': 123, 'test2': 456}
        fields = expect.keys()
        self._new_exporter(self.dns_id)._create_data(
            map_record, fields, **expect
        )
        map_record.values.assert_called_once_with(
            for_create=True, fields=fields, **expect
        )

    def test_create_data_return(self):
        """ It should inject proper vals into map record """
        map_record = mock.MagicMock()
        res = self._new_exporter(self.dns_id)._create_data(map_record)
        self.assertEqual(map_record.values(), res)

    def test_create_validates_data(self):
        """ It should validate data """
        expect = 'expect'
        exporter = self._new_exporter()
        with self.mock_base_exporter(exporter, ['_validate_create_data']):
            exporter._validate_create_data.side_effect = self.EndTestException
            with self.assertRaises(self.EndTestException):
                exporter._create(expect)
            exporter._validate_create_data.assert_called_once_with(expect)

    def test_create_does_create(self):
        """ It should create remote record w/ data """
        expect = 'expect'
        exporter = self._new_exporter()
        with self.mock_adapter(exporter) as mk:
            mk.create.side_effect = self.EndTestException
            with self.assertRaises(self.EndTestException):
                exporter._create(expect)
            mk.create.assert_called_once_with(expect)

    def test_create_returns_binding(self):
        """ It should return new binding """
        exporter = self._new_exporter()
        with self.mock_adapter(exporter) as mk:
            res = exporter._create(None)
            self.assertEqual(
                mk.create(), res
            )

    def test_update_data_call(self):
        """ It should inject proper vals into map record """
        map_record = mock.MagicMock()
        expect = {'test': 123, 'test2': 456}
        fields = expect.keys()
        self._new_exporter(self.dns_id)._update_data(
            map_record, fields, **expect
        )
        map_record.values.assert_called_once_with(fields=fields, **expect)

    def test_update_data_return(self):
        """ It should inject proper vals into map record """
        map_record = mock.MagicMock()
        res = self._new_exporter(self.dns_id)._update_data(map_record)
        self.assertEqual(map_record.values(), res)

    def test_update_does_write(self):
        """ It should update binding w/ data """
        expect = 'expect'
        mk = mock.MagicMock()
        exporter = self._new_exporter(dns_id=self.dns_id)
        with self.mock_adapter(exporter) as mk:
            mk.write.side_effect = self.EndTestException
            with self.assertRaises(self.EndTestException):
                exporter._update(expect)
            mk.write.assert_called_once_with(self.dns_id, expect)

    def test_run_assert_binding_id(self):
        """ It should assert existing binding_id """
        exporter = self._new_exporter(binding_record=True)
        with self.assertRaises(AssertionError):
            exporter._run()

    def test_run_assert_binding_id(self):
        """ It should assert existing binding_record """
        exporter = self._new_exporter(binding_id=True)
        with self.assertRaises(AssertionError):
            exporter._run()

    def test_run_has_to_skip(self):
        """ It should return None if _has_to_skip """
        exporter = self._new_exporter(binding_id=True, binding_record=True)
        with self.mock_base_exporter(exporter, ['_has_to_skip']):
            exporter._has_to_skip.return_value = True
            res = exporter._run()
            self.assertEqual(None, res)

    def test_run_export_dependencies(self):
        """ It should first export dependencies """
        exporter = self._new_exporter(binding_id=True, binding_record=True)
        with self.mock_base_exporter(exporter, ['_export_dependencies',
                                                '_has_to_skip',
                                                ]):
            exporter._has_to_skip.return_value = False
            exporter._export_dependencies.side_effect = self.EndTestException
            with self.assertRaises(self.EndTestException):
                exporter._run()

    def test_run_lock(self):
        """ It should call lock """
        exporter = self._new_exporter(binding_id=True, binding_record=True)
        with self.mock_base_exporter(exporter, ['_has_to_skip',
                                                '_lock',
                                                ]):
            exporter._has_to_skip.return_value = False
            exporter._lock.side_effect = self.EndTestException
            with self.assertRaises(self.EndTestException):
                exporter._run()

    def test_run_map_data(self):
        """ It should get map_data """
        exporter = self._new_exporter(binding_id=True, binding_record=True)
        with self.mock_base_exporter(exporter, ['_export_dependencies',
                                                '_has_to_skip',
                                                '_lock',
                                                '_map_data',
                                                ]):
            exporter._has_to_skip.return_value = False
            exporter._map_data.side_effect = self.EndTestException
            with self.assertRaises(self.EndTestException):
                exporter._run()

    def test_run_map_data(self):
        """ It should get map_data """
        exporter = self._new_exporter(binding_id=True, binding_record=True)
        with self.mock_base_exporter(exporter, ['_has_to_skip',
                                                '_lock',
                                                '_map_data',
                                                ]):
            exporter._has_to_skip.return_value = False
            exporter._map_data.side_effect = self.EndTestException
            with self.assertRaises(self.EndTestException):
                exporter._run()

    def test_run_update_data(self):
        """ It should identify data to update on pre-existing binds """
        exporter = self._new_exporter(self.dns_id, True, True)
        expect = ['test1', 'test2']
        with self.mock_base_exporter(exporter, ['_has_to_skip',
                                                '_lock',
                                                '_map_data',
                                                '_update_data',
                                                ]):
            exporter._has_to_skip.return_value = False
            exporter._update_data.side_effect = self.EndTestException
            with self.assertRaises(self.EndTestException):
                exporter._run(expect)
            exporter._update_data.assert_called_once_with(
                exporter._map_data(), fields=expect
            )

    def test_run_update_no_record(self):
        """ It should identify data to update on pre-existing binds """
        exporter = self._new_exporter(self.dns_id, True, True)
        with self.mock_base_exporter(exporter, ['_has_to_skip',
                                                '_lock',
                                                '_map_data',
                                                '_update_data',
                                                ]):
            exporter._has_to_skip.return_value = False
            exporter._update_data.return_value = False
            res = exporter._run()
            self.assertEqual(
                _('Nothing to export.'), res,
            )

    def test_run_update_no_record(self):
        """ It should identify data to update on pre-existing binds """
        exporter = self._new_exporter(self.dns_id, True, True)
        with self.mock_base_exporter(exporter, ['_has_to_skip',
                                                '_lock',
                                                '_map_data',
                                                '_update_data',
                                                '_update',
                                                ]):
            exporter._has_to_skip.return_value = False
            exporter._update.side_effect = self.EndTestException
            with self.assertRaises(self.EndTestException):
                exporter._run()
            exporter._update.assert_called_once_with(
                exporter._update_data()
            )

    def test_run_create_data(self):
        """ It should identify data to create on pre-existing binds """
        exporter = self._new_exporter(False, True, True)
        expect = ['test1', 'test2']
        with self.mock_base_exporter(exporter, ['_has_to_skip',
                                                '_lock',
                                                '_map_data',
                                                '_create_data',
                                                ]):
            exporter._has_to_skip.return_value = False
            exporter._create_data.side_effect = self.EndTestException
            with self.assertRaises(self.EndTestException):
                exporter._run(expect)
            exporter._create_data.assert_called_once_with(
                exporter._map_data(), fields=None
            )

    def test_run_create_no_record(self):
        """ It should identify data to create on pre-existing binds """
        exporter = self._new_exporter(False, True, True)
        with self.mock_base_exporter(exporter, ['_has_to_skip',
                                                '_lock',
                                                '_map_data',
                                                '_create_data',
                                                ]):
            exporter._has_to_skip.return_value = False
            exporter._create_data.return_value = False
            res = exporter._run()
            self.assertEqual(
                _('Nothing to export.'), res,
            )

    def test_run_create_no_record(self):
        """ It should identify data to create on pre-existing binds """
        exporter = self._new_exporter(False, True, True)
        with self.mock_base_exporter(exporter, ['_has_to_skip',
                                                '_lock',
                                                '_map_data',
                                                '_create_data',
                                                '_create',
                                                ]):
            exporter._has_to_skip.return_value = False
            exporter._create.side_effect = self.EndTestException
            with self.assertRaises(self.EndTestException):
                exporter._run()
            exporter._create.assert_called_once_with(
                exporter._create_data()
            )
