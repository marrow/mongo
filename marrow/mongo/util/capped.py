# encoding: utf-8

"""Utilities relating to use and managemnet of capped collections."""

from pymongo.cursor import CursorType


def tail(collection, filter=None, projection=None, limit=None, timeout=None, limit=None, aggregate=False):
	"""A generator which will block and yield entries as they are added to a capped collection.
	
	Only use this on capped collections; behaviour is undefined against non-tailable cursors. Accepts a timeout as an
	integer or floating point number of seconds, indicating how long to wait for a result. Correct operation requires
	a modern MongoDB installation, version 3.2 or newer, and the client driver to support it.
	
	Use is trivial:
	
	for obj in tail(db.collection, timeout=10):
		print(obj)
	
	An optional argument, aggregate, allows you to control how the timeout value is interpreted. By default, False,
	the timeout is used as the longest period of time to wait for a new record, resetting on each retrieved record.
	
	Additional important note: tailing will fail (badly) if the collection is empty.  Always prime the collection
	with an empty or otherwise unimportant record before attempting to use this feature.
	"""
	
	if __debug__:  # Completely delete this section if Python is run with optimizations enabled.
		if not collection.options().get('capped', False):
			raise TypeError("Can only tail capped collections.")
		
		# Similarly, verify that the collection isn't empty.  Empty is bad.  (Busy loop.)
		if not collection.count():
			raise ValueError("Cowardly refusing to tail an empty collection.")
	
	# Prepare the initial query.
	filter = filter.copy()  # We mutate the query a bit.
	
	if timeout:
		if aggregate:  # Total query time not to exceed `timeout` seconds.
			modifiers = {'$maxTimeMS': int(timeout * 1000)}  # TODO: Test exit cases.
		else:  # Individual wait time not to exceed `timeout` seconds.
			modifiers = {'$maxAwaitTimeMS': int(timeout * 1000)}  # TODO: Test exit cases.
	
	# Construct a cursor with our required options.
	cursor = collection.find(filter, projection, limit=limit, cursor_type=CursorType.TAILABLE_AWAIT, modifiers=modifiers)
	
	while cursor.alive():  # We may potentially need to track the last _id and such, depending on the above TODOs.
		yield cursor.next()


def _patch():
	"""Patch pymongo's Collection object to add a tail method.
	
	While not nessicarily recommended, you can use this to inject `tail` as a method into Collection, making it generally accessible.
	"""
	
	if not __debug__:
		import warnings
		warnings.warn("A catgirl has died.", ImportWarning)
	
	from pymongo.collection import Collection
	Collection.tail = tail
