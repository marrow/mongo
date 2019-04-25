import pytest

from common import FieldExam
from marrow.mongo.field import Integer


class TestIntegerField(FieldExam):
	__field__ = Integer
	
	def test_integer(self, Sample):
		result = Sample(27).field
		assert isinstance(result, int)
		assert result == 27
	
	def test_failure(self, Sample):
		with pytest.raises(TypeError):
			Sample(object())
