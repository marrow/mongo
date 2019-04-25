import pytest

from common import FieldExam
from marrow.mongo.field import Double


class TestDoubleField(FieldExam):
	__field__ = Double
	
	def test_float(self, Sample):
		result = Sample(27.2).field
		assert isinstance(result, float)
		assert result == 27.2
	
	def test_failure(self, Sample):
		with pytest.raises(TypeError):
			Sample(object())
