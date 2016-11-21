# encoding: utf-8
# pragma: no cover

"""Experimental Python standard logging support features.

This is untested and is subject to change, use at own risk.

Will utilize `pygments` syntax highlighting if available.

Example logging "dictconfig":

{
	'version': 1,
	'handlers': {
			'console': {
					'class': 'logging.StreamHandler',
					'formatter': 'json',
					'level': 'DEBUG' if __debug__ else 'INFO',
					'stream': 'ext://sys.stdout',
				}
		},
	'loggers': {
			'web': {
					'level': 'DEBUG' if __debug__ else 'WARN',
					'handlers': ['console'],
					'propagate': False,
				},
		},
	'root': {
			'level': 'INFO' if __debug__ else 'WARN',
			'handlers': ['console']
		},
	'formatters': {
			'json': {
					'()': 'marrow.mongo.util.logger.JSONFormatter',
				}
		},
}
"""

from __future__ import unicode_literals

import logging
import datetime
from bson.json_util import dumps
from pymongo import MongoClient
from pytz import utc
from tzlocal import get_localzone

try:
	from pygments import highlight as _highlight
	from pygments.formatters import Terminal256Formatter
	from pygments.lexers.data import JsonLexer
except ImportError:
	_highlight = None


DEFAULT_PROPERTIES = logging.LogRecord('', '', '', '', '', '', '', '').__dict__.keys()
LOCAL_TZ = get_localzone()


class JSONFormatter(logging.Formatter):
	REPR_FAILED = 'REPR_FAILED'
	BASE_TYPES = (int, float, bool, bytes, str, list, dict)
	EXCLUDE = {
		# Python 2/3
		'args', 'name', 'msg', 'levelname', 'levelno', 'pathname', 'filename',
		'module', 'exc_info', 'exc_text', 'lineno', 'funcName', 'created',
		'msecs', 'relativeCreated', 'thread', 'threadName', 'processName',
		'process', 'getMessage', 'message', 'asctime',
		
		# Python 3
		'stack_info',
	}
	
	def __init__(self, highlight=None, indent=False, **kwargs):
		if __debug__:
			format = "{created}\t{levelname}\t{name}:{funcName}:{lineno}\t{message}"
		else:
			format = "{levelname} {name}:{funcName}:{lineno} {message}"
		super(JSONFormatter, self).__init__(format, style='{')
		self.highlight = (__debug__ if highlight is None else highlight) and _highlight is not None
		self.indent = indent
	
	def _default(self, value):
		try:
			return str(value)
		except:
			try:
				return repr(value)
			except:
				return self.REPR_FAILED
	
	def jsonify(self, record, **kw):
		extra = {}
		
		for attr, value in record.__dict__.items():
			if attr in self.EXCLUDE: continue
			extra[attr] = value
		
		if extra:
			try:
				return dumps(extra, skipkeys=True, sort_keys=True, default=self._default, **kw)
			except Exception as e:
				return dumps({'__error': repr(e)}, **kw)
		
		return ''
	
	def format(self, record):
		try:
			record.message = record.getMessage()
		except Exception as e:
			record.message = "Something exploded trying to calcualte this message: " + repr(e)
		
		try:
			formatted = super(JSONFormatter, self).formatMessage(record)
		except Exception as e:
			formatted = "Something exploded trying to format this message: " + repr(e)
		
		try:
			json = self.jsonify(
				record,
				separators = (', ' if not self.indent else ',', ': ') if __debug__ else (',', ':'),
				indent = "\t" if self.indent else None,
			)
		except Exception as e:
			formatted = "JSON calculation failed: " + repr(e)
			json = None
		
		if json:
			if self.highlight:
				return '\n'.join([formatted, _highlight(json, JsonLexer(tabsize=4), Terminal256Formatter(style='monokai')).strip()])
			
			return '\n'.join([formatted, json]).strip()
		
		return formatted


class MongoFormatter(logging.Formatter):
	def format(self, record):
		time = datetime.datetime.fromtimestamp(record.created)
		time = LOCAL_TZ.localize(time).astimezone(utc)
		
		document = dict(
				service = record.name,
				level = record.levelno,
				message = record.getMessage(),  # TODO: super() this?
				
				time = time,
				process = dict(
						identifier = record.process,
						name = record.processName,
					),
				thread = dict(
						identifier = record.thread,
						name = record.threadName,
					),
				location = dict(
						path = record.pathname,
						line = record.lineno,
						module = record.module,
						function = record.funcName,
					),
			)
		
		if record.exc_info is not None:
			document['exception'] = dict(
					cls = record.exc_info[0].__name__,
					message = str(record.exc_info[1]),
					trace = self.formatException(record.exc_info)
				)
		
		# Standard document decorated with extra contextual information
		
		if len(DEFAULT_PROPERTIES) != len(record.__dict__):
			extras = set(record.__dict__).difference(set(DEFAULT_PROPERTIES))
			for name in extras:
				document[name] = record.__dict__[name]
		
		return document


class MongoHandler(logging.Handler):
	def __init__(self, uri, collection, level=logging.NOTSET, quiet=False):
		logging.Handler.__init__(self, level=level)
		
		if quiet:
			self.lock = None  # We don't require I/O locking if we aren't touching stderr.
		
		client = self.client = MongoClient(uri)
		database = client.get_default_database()
		self.collection = database[collection]
		
		self.buffer = []
		self.formatter = MongoFormatter()  # We default to our standard record encoding.
	
	def emit(self, record):
		try:
			document = self.format(record)
		except:
			self.handleError(record)
			return
		
		try:
			result = self.collection.insert_one(document)
		except:
			self.handleError(record)
			return
		
		document['_id'] = result.inserted_id
