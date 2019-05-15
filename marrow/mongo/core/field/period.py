from datetime import datetime, timedelta
from typing import Optional

from .date import Date
from ...util import utcnow, datetime_period
from ....schema import Attribute


class Period(Date):
	"""A specialized Date field used to store dates rounded down to the start of a given period."""
	
	hours: Optional[int] = Attribute(default=None)
	minutes: Optional[int] = Attribute(default=None)
	seconds: Optional[int] = Attribute(default=None)
	
	@property
	def delta(self) -> timedelta:
		return timedelta(hours=self.hours or 0, minutes=self.minutes or 0, seconds=self.seconds or 0)
	
	def to_foreign(self, obj, name: str, value) -> datetime:
		value = super(Period, self).to_foreign(obj, name, value)
		
		return datetime_period(value, hours=self.hours, minutes=self.minutes, seconds=self.seconds)
