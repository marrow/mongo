# encoding: utf-8

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
