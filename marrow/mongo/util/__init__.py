# encoding: utf-8


SENTINEL = object()  # Singleton value to detect unassigned values.


def adjust_attribute_sequence(amount=10000, *fields):
	"""Move marrow.schema fields around to control positional instantiation order."""
	
	def adjust_inner(cls):
		for field in fields:
			getattr(cls, field).__sequence__ += amount  # Move this to the back of the bus.
		return cls
	
	return adjust_inner



