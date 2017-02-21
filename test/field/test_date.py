# encoding: utf-8

from __future__ import unicode_literals

from common import FieldExam
from marrow.mongo.field import Date


class TestDateField(FieldExam):
	__field__ = Date
