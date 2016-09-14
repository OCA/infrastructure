# -*- coding: utf-8 -*-
# Copyright 2016 LasLabs Inc.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp.exceptions import ValidationError
from openerp.tests.common import TransactionCase


class TestDNSRecord(TransactionCase):

    def new_record(self):
        self.type = self.env.ref('connector_dns.type_a')
        self.zone = self.env['dns.zone'].create({'name': 'Zone'})
        return self.env['dns.record'].create({
            'name': 'Test',
            'zone_id': self.zone.id,
            'type_id': self.type.id,
            'value': '192.168.1.1',
        })

    def test_invalid_value(self):
        """ It should raise ValidationError on invalid value """
        record = self.new_record()
        with self.assertRaises(ValidationError):
            record.write({'value': 'Not an IP'})
