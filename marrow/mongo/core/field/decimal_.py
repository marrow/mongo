from decimal import Decimal as dec, localcontext

from ..types import Union
from .number import Number, NumberABC

try:
	from bson.decimal128 import Decimal128, create_decimal128_context

except ImportError:  # pragma: no cover
	Decimal = None

else:
	class Decimal(Number):
		__foreign__ = 'decimal'
		
		DECIMAL_CONTEXT = create_decimal128_context()
		
		def to_native(self, obj, name:str, value:Union[str,dec,Decimal128]) -> dec:  # pylint:disable=unused-argument
			if hasattr(value, 'to_decimal'):
				return value.to_decimal()
			
			if not isinstance(value, dec):
				with localcontext(self.DECIMAL_CONTEXT) as ctx:
					value = ctx.create_decimal(value)
			
			return value
		
		def to_foreign(self, obj, name:str, value:Union[str,dec]) -> Decimal128:  # pylint:disable=unused-argument
			if not isinstance(value, dec):
				with localcontext(self.DECIMAL_CONTEXT) as ctx:
					value = ctx.create_decimal(value)
			
			return Decimal128(value)
