# -*- coding: utf-8 -*-
# Copyright 2016 LasLabs Inc.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp.tests.common import TransactionCase


class TestDNSRecordType(TransactionCase):

    def setUp(self):
        super(TestDNSRecordType, self).setUp()
        self.record = self.env.ref('connector_dns.type_a')

    def test_name_get(self):
        """ It should conjoin code and name """
        self.assertEqual(
            '%s - %s' % (self.record.code, self.record.name),
            self.record.display_name,
        )
