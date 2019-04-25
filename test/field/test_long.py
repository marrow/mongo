from common import FieldExam
from marrow.mongo.field import Long


class TestLongField(FieldExam):
	__field__ = Long
	
	def test_biginteger(self, Sample):
		result = Sample(272787482374844672646272463).field
		assert result == 272787482374844672646272463
