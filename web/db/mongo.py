# encoding: utf-8

"""MongoDB database connection extension."""

import re

from pymongo import MongoClient
from pymongo.errors import ConfigurationError


log = __import__('logging').getLogger(__name__)

_safe_uri_replace = re.compile(r'(\w+)://(\w+):(?P<password>[^@]+)@')


class MongoDBConnection(object):
	__slots__ = ('__name__', 'uri', 'config', 'client', 'db')
	
	provides = {'mongodb'}
	
	def __init__(self, uri, **config):
		self.uri = uri
		self.client = None
		self.db = None
		self.config = config
	
	def start(self, context):
		log.info("Connecting context.db." + self.__name__ + " to MongoDB database.", extra=dict(
				uri = _safe_uri_replace.sub(r'\1://\2@', self.uri),
				config = self.config,
			))
		
		client = self.client = MongoClient(self.uri, **self.config)
		
		try:
			db = self.db = client.get_default_database()
		except ConfigurationError:
			db = self.db = None
		
		context.db[self.__name__] = db if db is not None else client

