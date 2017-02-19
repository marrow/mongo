# encoding: utf-8

from __future__ import unicode_literals

import pytest

from marrow.mongo import Document
from marrow.mongo.core.field.path import _Path
from marrow.mongo.field import Path
from marrow.schema.compat import unicode


class Sample(Document):
	path = Path()


class TestPathField(object):
	def test_native_conversion(self):
		inst = Sample.from_mongo({'path': '/foo'})
		value = inst.path
		assert isinstance(value, _Path)
		assert unicode(value) == '/foo'
	
	def test_foreign_conversion(self):
		inst = Sample(_Path('/bar'))
		assert isinstance(inst['path'], unicode)
		assert inst['path'] == '/bar'
