# encoding: utf-8


class Person(Document):
	name = String()
	age = Number()
	tag = Array(String())


class Statistics(Document):
	comments = Integer()
	uploads = Integer()
	votes = Integer()
	views = Integer()


class Forum(Document):
	id = String('_id')  # Slug
	name = String()
	summary = String()
	
	# Permission tags.
	read = String()
	write = String()
	moderate = String()
	
	stat = Embed(Statistics)
	
	modified = Date()


class Votes(Document):
	count = Long()
	who = Array(ObjectId())


class Comment(Document):
	id = ObjectId(generate=True)
	message = String()
	vote = Embed(Votes)
	creator = ObjectId()  # User is, ah, defined somewhere else.  Yeah.  We'll go with that.
	updated = Date(now=True)
	uploads = Array(ObjectId())  # GridFS files.


class Continuation(Document):
	continued = Reference()


class Flags(Document):
	locked = Boolean()
	sticky = Boolean()
	hidden = Boolean()
	uploads = Boolean()


class Thread(Document):
	title = String()
	forum = Reference()
	
	comments = Array(Embed(Comment, Continuation))
	
	flag = Embed(Flags)
	stat = Embed(Statistics)
	
	subs = Array(ObjectId())
	updated = Date(now=True)


