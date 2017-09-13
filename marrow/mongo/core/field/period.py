# encoding: utf-8

from __future__ import unicode_literals

from datetime import timedelta

from .date import Date
from ...util import utcnow, datetime_period
from ....schema import Attribute


class Period(Date):
	"""A specialized Date field used to store dates rounded down to the start of a given period."""
	
	hours = Attribute(default=None)
	minutes = Attribute(default=None)
	seconds = Attribute(default=None)
	
	@property
	def delta(self):
		return timedelta(hours=self.hours or 0, minutes=self.minutes or 0, seconds=self.seconds or 0)
	
	def to_foreign(self, obj, name, value):
		value = super(Period, self).to_foreign(obj, name, value)
		
		return datetime_period(value, hours=self.hours, minutes=self.minutes, seconds=self.seconds)
