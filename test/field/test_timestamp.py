# encoding: utf-8

from __future__ import unicode_literals

from common import FieldExam
from marrow.mongo.field import Timestamp


class TestTimestampField(FieldExam):
	__field__ = Timestamp
