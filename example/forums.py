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
from marrow.mongo.field import String, Integer, Array, Embed, Boolean
from marrow.mongo.trait import Identified, Queryable


class Statistics(Document):
	comments = Integer()
	uploads = Integer()
	votes = Integer()
	views = Integer()


class Reply(Document):
	pass


class Person(Queryable):
	__collection__ = 'people'
	
	name = String()
	tag = Array(String())


class Forum(Queryable):
	__collection__ = 'forums'
	
	id = String('_id')  # Redefine the primary key as a string slug.
	name = String()
	summary = String()
	
	# Permission tagsefer
	read = String()
	write = String()
	moderate = String()
	
	stat = Embed(Statistics)
	
	modified = Date()


class Thread(Queryable):
	__collection__ = 'threads'
	
	class Flags(Document):
		locked = Boolean()
		sticky = Boolean()
		hidden = Boolean()
		uploads = Boolean()
	
	class Comment(Identified, Reply):
		class Votes(Document):
			count = Integer()
			who = Array(ObjectId())
		
		id = ObjectId('_id')
		message = String()
		vote = Embed(Votes)
		creator = ObjectId()
		updated = Date(default=utcnow, assign=True)
		uploads = Array(ObjectId())  # GridFS file references.
	
	class Continuation(Reply):
		continued = Reference()
	
	title = String()
	forum = Reference()
	
	replies = Array(Embed(Reply))
	
	flag = Embed(Flags)
	stat = Embed(Statistics)
	
	subscribers = Array(ObjectId())
	updated = Date(default=utcnow, assign=True)
