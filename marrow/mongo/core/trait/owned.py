# encoding: utf-8

"""Data model trait mix-in for tracking record ownership."""

from ... import Document, Index
from ...field import Reference


class Owned(Document):
	"""Record ownership abstraction.
	
	This adds two fields to any given document it is mixed into, company, and creator, and an index on creator.
	"""
	
	# ## Ownership / Management Fields
	
	creator = Reference()
	
	_creator = Index('creator')