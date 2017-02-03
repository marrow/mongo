# encoding: utf-8

from ... import Document, Index
from ...field import ObjectId, String, Path, Array, Alias


class Heirarchical(Document):
	"""Record sufficient information to form a heirarchy of documents."""
	
	# ## Heirarchy Field Definition
	
	slug = String(required=True)  # A short, lower-case identifier.
	path = Path(required=True)  # The coalesced path to the document.
	parents = Array(ObjectId(), default=lambda: [], assign=True)
	
	parent = Alias('parents.-1', default=None)  # The immediate parent.
	
	# ## Index Definitions
	
	_path = Index('path', unique=True)
	_parents = Index('parents')
