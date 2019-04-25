from decimal import Decimal as dec

from bson.decimal128 import Decimal128

from common import FieldExam
from marrow.mongo.field import Decimal


class TestDecimalField(FieldExam):
	__field__ = Decimal
	
	def test_decimal(self, Sample):
		v = dec('3.141592')
		result = Sample(v)
		assert isinstance(result['field'], Decimal128)
		assert result['field'] == Decimal128('3.141592')
		assert result.field == v
	
	def test_decimal_cast_up(self, Sample):
		result = Sample.from_mongo({'field': 27.4})
		v = result.field
		assert isinstance(v, dec)
		assert float(v) == 27.4
	
	def test_decimal_from_number(self, Sample):
		result = Sample(27)
		assert isinstance(result['field'], Decimal128)
		assert result['field'] == Decimal128('27')
		assert int(result.field) == 27
