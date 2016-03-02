# encoding: utf-8

"""A sample data model to perform analytics across."""

from random import randint, choice

from marrow.mongo.core import Document
from marrow.mongo.field.registry import String, Date, Boolean, Number, Array

from .helper import enum



class Item(Document):
	label = String()
	price = Number()
	
	def __repr__(self):
		return 'Item("{self.label}", ${self.price})'.format(self)
	
	def __str__(self):
		return self.label
	
	def __float__(self):
		return self.price


# One might have different types of Item subclasses.  Like PurchaseItem, TaxItem, etc.


class Total(Document):
	price = Number(default=0)
	total = Number(default=0)
	
	def __repr__(self):
		return 'Total({self.total}, price={self.price})'.format(self)
	
	def __float__(self):
		return self.total
	
	@classmethod
	def from_items(cls, items):
		self = cls()
		
		for item in self.items:
			self.price += item.price
		
		# Pretend there were taxes or something.
		
		self.total = self.price
		
		return self


class Invoice(Document):
	STATE = enum('InvoiceState', 'incomplete', 'pending', 'accepted', 'complete', 'invoiced', 'paid', 'void', 'hidden')
	
	state = String(choices=STATE, default='incomplete')
	
	items = Array(Item, default=list)
	totals = Embed(Total)
	
	modified = Date(now=True)


def _populate(collection):
	"""Create a bunch of random invoices."""
	
	for i in range(1000):
		inv = Invoice(state=choice(Invoice.STATE))
		
		for j in range(randint(1, 5)):
			inv.items.append(Item("Random Line Item", randint(0, 10000) * 0.01))
		
		inv.total = Total.from_items(inv.items)
		collection.insert_one(inv.__data__)
