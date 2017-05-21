# encoding: utf-8

from __future__ import unicode_literals

from decimal import Decimal as dec, localcontext

from .number import Number

try:
	from bson.decimal128 import Decimal128, create_decimal128_context

except ImportError:  # pragma: no cover
	Decimal = None

else:
	class Decimal(Number):
		__foreign__ = 'decimal'
		
		DECIMAL_CONTEXT = create_decimal128_context()
		
		def to_native(self, obj, name, value):  # pylint:disable=unused-argument
			if hasattr(value, 'to_decimal'):
				return value.to_decimal()
			
			return dec(value)
		
		def to_foreign(self, obj, name, value):  # pylint:disable=unused-argument
			if not isinstance(value, dec):
				with localcontext(self.DECIMAL_CONTEXT) as ctx:
					value = ctx.create_decimal(value)
			
			return Decimal128(value)
