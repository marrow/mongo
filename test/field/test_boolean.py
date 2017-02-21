# encoding: utf-8

from __future__ import unicode_literals

import pytest

from common import FieldExam
from marrow.mongo.field import Boolean


class TestBooleanField(FieldExam):
	__field__ = Boolean
	
	def test_cast_boolean(self, Sample):
		inst = Sample(True)
		assert inst.field is True
		
		inst = Sample(False)
		assert inst.field is False
	
	def test_cast_strings(self, Sample):
		inst = Sample("true")
		assert inst.field is True
		
		inst = Sample("false")
		assert inst.field is False
	
	def test_cast_none(self, Sample):
		inst = Sample(None)
		assert inst.field is None
	
	def test_cast_other(self, Sample):
		inst = Sample(1)
		assert inst.field is True
	
	def test_cast_failure(self, Sample):
		with pytest.raises(ValueError):
			Sample('hehehe')
