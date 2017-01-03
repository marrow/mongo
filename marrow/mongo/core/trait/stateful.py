# encoding: utf-8

from ... import Document
from ...field import String


class Stateful(Document):
	"""A document trait for state transition management."""
	
	__states__ = {}
	__transitions__ = {}
	
	state = String()