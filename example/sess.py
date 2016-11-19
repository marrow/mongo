# encoding: utf-8

from web.core import Application
from web.ext.debug import DebugExtension
from web.ext.db import DatabaseExtension
from web.db.mongo import MongoDBConnection
from web.ext.session import SessionExtension
from web.session.mongo import MongoSession, MongoSessionStorage
from marrow.mongo.field import String


class Session(MongoSessionStorage):
	__collection__ = 'sessions'
	
	value = String(default=None)


class Root(object):
	def __init__(self, context):
		self._ctx = context
	
	def get(self):
		return repr(self._ctx.session.__data__)
	
	def set(self, value):
		self._ctx.session.value = value
		return "OK"


app = Application(Root, extensions=[
		DebugExtension(),
		DatabaseExtension(session=MongoDBConnection('mongodb://localhost/test')),
		SessionExtension(
			secret = 'xyzzy',
			expires = 24 * 90,
			default = MongoSession(Session, database='session'),
		),
	])


if __name__ == "__main__":
	app.serve('wsgiref', host='0.0.0.0', port=8080)
