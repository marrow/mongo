"""Example discussion forums representation.

We attempt to make use of the best of both (relational and document) worlds. We track forums as distinct records, and
threads within those forums separately. The replies to a thread are then stored within the threads themselves. Various
statistics can be gathered.

You may be thinking to yourself that MongoDB records have a limited size, and you'd be right. 16MiB is the largest
record size as of this writing. Consider how much text that represents, though! It's around 500 novel chapters. While
this is not entirely reasonable for even a very large and active group to compose within a single thread, we can still
account for it by providing "continuation" markers to point at the next thread record to continue using from there.
"""

from marrow.mongo import Document, Index, utcnow
from marrow.mongo.field import Array, Boolean, Embed, Integer, Markdown, Set, String
from marrow.mongo.trait import Derived, Identified, Queryable


class Statistics(Document):
	"""General discussion statistics.
	
	These are replicated within each tier of record to represent aggregated statistics.
	"""
	
	comments = Integer(default=0, assign=True)
	uploads = Integer(default=0, assign=True)
	votes = Integer(default=0, assign=True)
	views = Integer(default=0, assign=True)


class Reply(Derived, Identified):
	...  # Subclasses define relevant additioanl attributes; treat this as an ABC.


class Person(Queryable):
	__collection__ = 'people'
	
	name = String()
	tag = Array(String())


class Forum(Queryable):
	__collection__ = 'forums'
	
	id = String('_id')  # Redefine the primary key as a string slug.
	title = String()  # The human-readable name.
	summary = Markdown()  # A formatted description of the forum.
	
	# Permission Tags
	read = Set(String(), assign=True)  # User must have one of these tags to be able to read this forum.
	write = Set(String(), assign=True)  # As above, to be able to post or reply.
	moderate = Set(String(), assign=True)  # As above, but to access moderator privelages such as locking and trnasfer.
	
	stat = Embed(Statistics, assign=True)  # We pre-allocate zeroes to prevent record resizing and movement later.
	
	created = Date(assign=True)  # As we're not using ObjectIds, we need to track this ourselves.
	modified = Date()


class Thread(Queryable):
	__collection__ = 'threads'
	
	class Flags(Document):
		locked = Boolean(default=False)
		sticky = Boolean(default=False)
		hidden = Boolean(default=False)
		uploads = Boolean(default=False)
	
	class Comment(Reply):
		class Votes(Document):
			count = Integer(default=0, assign=True)
			who = Array(ObjectId())
		
		message = Markdown()
		vote = Array(Embed(Votes), assign=True)
		creator = Reference(Person, cache={'name'})
		updated = Date(default=utcnow, assign=True)
		uploads = Array(ObjectId())  # GridFS file references.
	
	class Continuation(Reply):
		continued = Reference(Thread)
	
	title = String()
	forum = Reference(Forum)
	
	replies = Array(Embed(Reply))
	
	flag = Embed(Flags, assign=True)
	stat = Embed(Statistics, assign=True)
	
	subscribers = Array(ObjectId())
	modified = Date(default=utcnow, assign=True)
