# encoding: utf-8

"""MongoDB database connection extension."""

import re

from webob import request
from bson import json_util
from pymongo import MongoClient
from pymongo.errors import ConfigurationError
from gridfs.grid_file import GridOut

from .model import Model
from .resource import MongoDBResource
from .collection import MongoDBCollection
from .grid import render_grid_file


__all__ = ['Model', 'MongoDBResource', 'MongoDBCollection', 'MongoDBConnection']

log = __import__('logging').getLogger(__name__)

_safe_uri_replace = re.compile(r'(\w+)://(\w+):(?P<password>[^@]+)@')


class MongoDBConnection(object):
	"""WebCore database extension connector for MongoDB databases.
	
	This tiny class performs the work needed to populate the WebCore context with a MonogoDB database (or connection
	if no default database is provided) on startup, using `pymongo`. In addition to performing initial configuration,
	this extension adapts 
	"""
	
	__slots__ = ('__name__', 'uri', 'config', 'client', 'db', 'alias', 'minimum')
	
	provides = {'mongodb'}
	
	def __init__(self, uri, alias=None, minimum_version=None, **config):
		"""Prepare MongoDB client configuration.
		
		The only required configuration option (passed positionally or by keyword) is `uri`, specifying the host to
		connect to and optionally client credentials (username, password), default database, optional minimum server
		version defined as a version tuple, and additional options.  The minimum version will be checked immeiately
		upon startup.
		
		Extraneous keyword arguments will be stored and passed through to the `MongoClient` class instantiated on
		startup.
		"""
		self.uri = uri
		self.client = None
		self.db = None
		self.minimum = minimum_version
		self.alias = alias
		
		# Configure a few of our own defaults here, usually because we compare the value somewhere.
		config.setdefault('event_listeners', [])  # For logging purposes, we add some of our own handlers.
		
		self.config = config
	
	def start(self, context):
		name = self.alias or self.__name__  # Either we were configured with an explicit name, or the DB ext infers.
		
		request.json = json_util
		
		log.info("Connecting context.db.{name} to MongoDB database.".format(name=name), extra=dict(
				uri = _safe_uri_replace.sub(r'\1://\2@', self.uri),
				config = self.config,
			))
		
		client = self.client = MongoClient(self.uri, **self.config)
		
		if self.minimum:
			version = tuple(client.server_info()['version'].split('.'))
			if version < self.minimum:
				raise RuntimeError("Unsupported MongoDB server version: " + ".".join(version))
		
		try:
			db = self.db = client.get_default_database()
		except ConfigurationError:
			db = self.db = None
		
		if self.config.get('connect', True):
			pass  # Log extra details about the connection here.
		
		context.db[name] = db if db is not None else client
		
		if GridOut not in context.view:  # Register the GridFS handler if not already present.
			context.view.register(GridOut, render_grid_file)
	
	def stop(self, context):
		self.client.close()
		del context.db[self.alias or self.__name__]

