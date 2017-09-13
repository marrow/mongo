# encoding: utf-8

"""Marrow Mongo Date field specialization.

Commentary on high-level management of timezone casting:

	https://groups.google.com/forum/#!topic/mongodb-user/GOMjTJON4cg
"""

from __future__ import unicode_literals

from datetime import datetime, timedelta, tzinfo
from bson import ObjectId as OID
from collections import MutableMapping
from datetime import datetime, timedelta

from .base import Field
from ...util import utc, utcnow
from ....schema import Attribute

# Conditional dependencies.

try:
	from pytz import timezone as get_tz
except ImportError:
	get_tz = None

try:
	localtz = __import__('tzlocal').get_localzone()
except ImportError:
	localtz = None


log = __import__('logging').getLogger(__name__)


class Date(Field):
	"""MongoDB date/time storage.
	
	Accepts the following options in addition to the base Field options:
	
	`naive`: The timezone to interpret assigned "naive" datetime objects as.
	`timezone`: The timezone to cast objects retrieved from the database to.
	
	Timezone references may be, or may be a callback returning, a `tzinfo`-suitable object, the string name of a
	timezone according to `pytz`, the alias 'naive' (strip or ignore the timezone) or 'local' (the local host's)
	timezone explicitly. None values imply no conversion.
	
	All dates are converted to and stored in UTC for storage within MongoDB; the original timezone is lost. As a
	result if `naive` is `None` then assignment of naive `datetime` objects will fail.
	"""
	
	__foreign__ = 'date'
	__disallowed_operators__ = {'#array'}
	
	naive = Attribute(default=utc)  # Timezone to interpret naive datetimes as.
	tz = Attribute(default=None)  # Timezone to cast to when retrieving from the database.
	
	def _process_tz(self, dt, naive, tz):
		"""Process timezone casting and conversion."""
		
		def _tz(t):
			if t in (None, 'naive'):
				return t
			
			if t == 'local':
				if __debug__ and not localtz:
					raise ValueError("Requested conversion to local timezone, but `localtz` not installed.")
				
				t = localtz
			
			if not isinstance(t, tzinfo):
				if __debug__ and not localtz:
					raise ValueError("The `pytz` package must be installed to look up timezone: " + repr(t))
				
				t = get_tz(t)
			
			if not hasattr(t, 'normalize') and get_tz:  # Attempt to handle non-pytz tzinfo.
				t = get_tz(t.tzname(dt))
			
			return t
		
		naive = _tz(naive)
		tz = _tz(tz)
		
		if not dt.tzinfo and naive:
			if hasattr(naive, 'localize'):
				dt = naive.localize(dt)
			else:
				dt = dt.replace(tzinfo=naive)
		
		if not tz:
			return dt
		
		if hasattr(tz, 'normalize'):
			dt = tz.normalize(dt.astimezone(tz))
		elif tz == 'naive':
			dt = dt.replace(tzinfo=None)
		else:
			dt = dt.astimezone(tz)  # Warning: this might not always be entirely correct!
		
		return dt
	
	def to_native(self, obj, name, value):
		if not isinstance(value, datetime):
			log.warning("Non-date stored in {}.{} field.".format(self.__class__.__name__, self.__name__),
					extra={'document': obj, 'field': self.__name__, 'value': value})
			return value
		
		return self._process_tz(value, self.naive, self.tz)
	
	def to_foreign(self, obj, name, value):  # pylint:disable=unused-argument
		if isinstance(value, MutableMapping) and '_id' in value:
			value = value['_id']
		
		if isinstance(value, OID):
			value = value.generation_time
		
		elif isinstance(value, timedelta):
			value = utcnow() + value
		
		if not isinstance(value, datetime):
			raise ValueError("Value must be a datetime, ObjectId, or identified document, not: " + repr(value))
		
		return self._process_tz(value, self.naive, utc)
