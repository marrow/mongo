from decimal import Decimal as dec, localcontext

from ..types import Any, Union, check_argument_types
from .number import Number, NumberABC

try:
	from bson.decimal128 import Decimal128, create_decimal128_context

except ImportError:  # pragma: no cover
	Decimal = None

else:
	class Decimal(Number):
		__foreign__ = 'decimal'
		
		DECIMAL_CONTEXT = create_decimal128_context()
		
		def to_native(self, obj, name:str, value:Union[str,dec,Decimal128,float]) -> dec:  # pylint:disable=unused-argument
			assert check_argument_types()
			
			if isinstance(value, Decimal128):
				return value.to_decimal()
			
			with localcontext(self.DECIMAL_CONTEXT) as ctx:
				return ctx.create_decimal(str(value))
		
		def to_foreign(self, obj, name:str, value:Union[str,dec,Decimal128,float,Any]) -> Decimal128:  # pylint:disable=unused-argument
			assert check_argument_types()
			
			if hasattr(value, 'to_decimal'):
				value = value.to_decimal()
			
			elif hasattr(value, 'as_decimal'):
				value = value.as_decimal
			
			if not isinstance(value, dec):
				with localcontext(self.DECIMAL_CONTEXT) as ctx:
					value = ctx.create_decimal(value)
			
			return Decimal128(value)
