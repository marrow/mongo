# encoding: utf-8

"""Data model trait mix-in for tracking record ownership."""

from ... import Document, Index
from ...field import Reference


class Owned(Document):
	owner = Reference()
	
	_owner = Index('owner')
