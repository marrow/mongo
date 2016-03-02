# encoding: utf-8

from __future__ import unicode_literals

from pymongo import ReadPreference

from .model import Invoice, _populate
from .heper import enum, sum, dur, daterange, difference


class InvoiceStats:
	INVALID_STATES = enum('incomplete', 'pending', 'void', 'hidden')
	
	def __init__(self, context):
		self._ctx = context
		self._collection = context.mongo.invoices.with_options(read_preference=ReadPreference.SECONDARY)
	
	def last(self, duration):
		"""Count of valid invoices during period.
		
		/invoice/last/<period>
		"""
		
		collection = self._collection
		duration, label = dur(duration)
		
		query = Invoice.state not in self.INVALID_STATES
		current, previous = daterange(duration, query)
		
		return difference(
				collection.count(current.as_query),
				collection.count(previous.as_query),
				str(label).format("Orders")
			)
	
	def count(self, state='any'):
		if state == 'any':
			return value(self._collection.count(), "Total Invoices")
		
		return value(self._collection.count(Invoice.state == state), state.title() + " Invoices")
	
	def revenue(self, duration):
		duration, label = dur(duration)
		current, previous = daterange(duration, Invoice.state not in self.INVALID_STATES)
		
		return difference(
				sum(collection, current.as_query, Invoice.total.total),
				sum(collection, previous.as_query, Invoice.total.total)
				label.format("Revenue")
			)


class Root:
	invoice = InvoiceStats
	
	def populate(self):
		_populate()
		return dict(success=True)
