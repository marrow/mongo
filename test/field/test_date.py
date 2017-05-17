# encoding: utf-8

from __future__ import unicode_literals

from datetime import datetime

from bson import ObjectId
from common import FieldExam
from marrow.mongo.field import Date


class TestDateField(FieldExam):
	__field__ = Date
	
	def test_date_like_oid(self, Sample):
		oid = ObjectId('586846800000000000000000')
		
		assert Sample(oid).field.replace(tzinfo=None) == datetime(2017, 1, 1)
