# encoding: utf-8

from ... import Document, Index
from ...field import String, Array, Embed
from ....schema import Attribute, Attributes


class State(Attribute):
	"""A vertex in the graph of states."""
	
	pass


class Transition(Attribute):
	"""A directed edge in the graph of states."""
	
	previous = Attribute()
	next = Attribute()


class Stateful(Document):
	"""A document trait for state transition management."""
	
	__states__ = Attributes(State)
	__transitions__ = Attributes(Transition)
	
	state = String(default=None)
	
	_state = Index('state')
	
	@property
	def __valid_transitions__(self):
		state = self.__states__[self.state] if self.state else None
		
		for transition in self.__transitions__.values():
			if transition.previous is state:
				yield transition
