from marrow.mongo.util import datetime_period, utcnow


class TestDatetimePeriod:
	def test_assumed_base(self):
		now = utcnow()
		then = datetime_period(hours=1)
		assert now.replace(minute=0, second=0) == then
