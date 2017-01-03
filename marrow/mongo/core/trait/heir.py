# encoding: utf-8

from ... import Document, Index
from ...field import ObjectId, String, Array


class Heirarchical(Document):
	"""Record sufficient information to form a heirarchy of documents."""
	
	# ## Heirarchy Field Definition
	
	slug = String(required=True)  # A short, lower-case identifier.
	path = String()  # The coalesced path to the document.
	parents = Array(ObjectId(), default=lambda: [], assign=True)
	
	# ## Index Definitions
	
	_path = Index('path', unique=True)
	_parents = Index('parents')
	
	# ## Accessor Properties
	
	@property
	def parent(self):  # TODO: Use Alias...
		return self.parents[-1] if self.parents else None