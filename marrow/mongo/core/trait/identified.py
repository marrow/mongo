# encoding: utf-8

from ... import Document
from ...field import ObjectId


class Identified(Document):
	"""A document utilizing this trait mix-in contains a MongoDB _id key.
	
	This provides a read-only property to retrieve the creation time as `created`.
	
	Identifiers are constructed on document instantiation; this means inserts are already provided an ID, bypassing
	the driver's behaviour of only returning one after a successful insert. This allows for the pre-construction
	of graphs of objects prior to any of them being saved, though, until all references are resolveable, the data
	is effectively in a broken, inconsistent state.  (Use bulk updates and plan for rollback in the event of failure!)
	
	No need for an explicit index on this as MongoDB will provide one automatically.
	"""
	
	__pk__ = 'id'
	
	id = ObjectId('_id', assign=True, write=False, repr=False)
	
	def __eq__(self, other):
		"""Equality comparison between the IDs of the respective documents."""
		
		if isinstance(other, Document):
			return self.id == other.id
		
		return self.id == other
	
	def __ne__(self, other):
		"""Inverse equality comparison between the backing store and other value."""
		
		if isinstance(other, Document):
			return self.id != other.id
		
		return self.id != other
