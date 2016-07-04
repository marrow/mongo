# encoding: utf-8

"""This is the Field registry.

It's scary, scary code, but basically you just import fields from the marrow.mongo namespace directly.

Fields with unambiguous suffixes (i.e. foo.Bar, foo.Baz) will be made available directly by their suffix (and with
their prefix) and ambiguous ones will be stored in sub-modules based on prefix. Only one level of prefix is permitted.
Only core field types are allowed to omit a prefix. (In development we check.) In ambiguous cases the core field type
will always "win".

Since the built-in fields follow the `marrow.mongo.field` plugin protocol the core fields are themselves made
available this way.

	from marrow.mongo import String, 
"""

from __future__ import unicode_literals

import imp
import sys

from marrow import mongo as TOP_LEVEL  # TODO: Move into function to isolate scope.
from marrow.package.host import PluginManager



class FieldRegistry(PluginManager):
	def register(self, name, plugin):
		from marrow import mongo as TOP_LEVEL
		
		super(FieldRegistry, self).register(name, plugin)
		namespace, name = name.partition('.') if '.' in name else ('', name)
		
		if name not in TOP_LEVEL.__dict__:
			TOP_LEVEL.__dict__[name] = plugin
		
		if namespace not in TOP_LEVEL.__dict__:
			namespace = TOP_LEVEL.__dict__[namespace] = sys.modules['marrow.mongo.' + namespace] = \
					imp.new_module(namespace)
		else:
			namespace = TOP_LEVEL.__dict__[namespace]
		
		





