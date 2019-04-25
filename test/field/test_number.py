import pytest

from common import FieldExam
from marrow.mongo.field import Number


class TestNumberField(FieldExam):
	__field__ = Number
	
	def test_passthrough(self, Sample):
		inst = Sample()
		inst.field = 42.1
		assert inst.field == 42.1
	
	def test_integer(self, Sample):
		result = Sample('27').field
		assert isinstance(result, int)
		assert result == 27
	
	def test_float(self, Sample):
		result = Sample('27.2').field
		assert isinstance(result, float)
		assert result == 27.2
	
	def test_failure(self, Sample):
		with pytest.raises(TypeError):
			Sample(object())
