# encoding: utf-8

"""This is the Field registry.

It's scary, scary code, but basically you just import fields from the marrow.mongo namespace directly.

Fields with unambiguous suffixes (i.e. foo.Bar, foo.Baz) will be made available directly by their suffix (and with
their prefix) and ambiguous ones will be stored in sub-modules based on prefix. Only one level of prefix is permitted.
Only core field types are allowed to omit a prefix. (In development we check.) In ambiguous cases the core field type
will always "win".

Since the built-in fields follow the `marrow.mongo.field` plugin protocol the core fields are themselves made
available this way.

	from marrow.mongo import String, ...
"""

from __future__ import unicode_literals

import imp
import sys

from marrow.package.host import PluginManager



class Registry(PluginManager):
	def __init__(self, top_level, namespace=None):
		self.top_level = top_level
		super(Registry, self).__init__(namespace or top_level.replace(':', '.'))
	
	def register(self, name, plugin):
		parent, _, module = self.top_level.partition(':')
		TOP_LEVEL = getattr(__import__(parent, fromlist=(module,)), module)
		
		super(Registry, self).register(name, plugin)
		namespace, name = name.partition('.') if '.' in name else ('', name)
		
		if name not in TOP_LEVEL.__dict__:
			TOP_LEVEL.__dict__[name] = plugin
		
		if namespace not in TOP_LEVEL.__dict__:
			TOP_LEVEL.__dict__[namespace] = sys.modules['marrow.mongo.field.' + namespace] = namespace = \
					imp.new_module(namespace)
		else:
			namespace = TOP_LEVEL.__dict__[namespace]
		
		namespace.__dict__[name] = plugin

