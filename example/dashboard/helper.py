# encoding: utf-8

from __future__ import unicode_literals

from bson import ObjectId as oid
from datetime import datetime, timedelta

from marrow.mongo.field import ObjectId
from marrow.mongo.util.compat import str


pk = ObjectId(name='_id')


DURATIONS = dict(
		day = (timedelta(days=1), "{} in the Last 24 Hours"),
		week = (timedelta(days=7), "{} in the Last 7 Days"),
		month = (timedelta(days=30), "{} in the Last 30 Days"),
		quarter = (timedelta(days=90), "{} in the Last 90 Days"),
		year = (timedelta(days=365), "{} in the Last 365 Days"),
	)


class Enum:
	def __iter__(self):
		iter(self._choices)


def enum(name, *choices):
	obj = dict(_choices=choices)
	
	for k in choices:
		if isinstance(k, tuple):
			obj[k[0]] = k[1]
		else:
			obj[k] = k
	
	return type(name, (Enum, ), obj)()


def sum(collection, filter, field):
	return list(collection.aggregate([
			{'$match': filter},
			{'$project': {_id: 0, _key: "$" + str(field)}},
			{'$group': {
				'_id': 1,
				'_sum': {'$sum': '$_key'}
			}}
		]))[0]['_sum']


def dur(duration):
	if duration not in DURATIONS:
		raise ValueError("Unknown duration: " + duration)
	
	return DURATIONS[duration]


def daterange(duration):
	now = datetime.utcnow()
	
	current = pk > oid.from_datetime(now - duration)
	previous = (pk > oid.from_datetime(now - duration * 2)) & (pk < oid.from_datetime(now - duration))
	
	return current, previous


def millis(delta):
	return (((24 * 60 * 60 * delta.days) + delta.seconds) * 1000000 + delta.microseconds) / 1000.0


def value(value, postfix):
	return dict(data=dict(value=value), postfix=str(postfix))


def difference(current, previous, postfix):
	return dict(data=[dict(value=current), dict(value=previous)], postfix=str(postfix))


def pie(items):
	return dict(data=[dict(name=str(i[1]), value=i[0]) for i in sorted(items, reverse=True)])


def list(items, label, kind):
	return dict(
			valueNameHeader = str(label),
			valueHeader = str(kind),
			data = [dict(name=str(i[1]), value=i[0]) for i in sorted(items, reverse=True)]
		)
