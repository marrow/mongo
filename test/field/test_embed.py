# encoding: utf-8

from __future__ import unicode_literals

import pytest

from common import FieldExam
from marrow.mongo import Document
from marrow.mongo.field import Embed, String
from marrow.mongo.trait import Derived


class Concrete(Derived, Document):
	__collection__ = 'collection'
	
	foo = String()
	bar = String()


class TestSingularEmbedField(FieldExam):
	__field__ = Embed
	__args__ = (Concrete, )
	
	def test_native_ingress(self, Sample):
		inst = Sample.from_mongo({'field': Concrete(foo=27, bar=42)})
		assert isinstance(inst.field, Concrete)
	
	def test_native_ingress_cast(self, Sample):
		inst = Sample.from_mongo({'field': {'foo': 27, 'bar': 42}})
		assert isinstance(inst.field, Concrete)
		assert inst.field.foo == 27
		assert inst.field.bar == 42
	
	def test_native_egress_cast(self, Sample):
		inst = Sample(field=Concrete())
		assert isinstance(inst.field, Concrete)
	
	def test_foreign_assignment_cast(self, Sample):
		inst = Sample()
		inst.field = {}
		assert isinstance(inst['field'], Concrete)
	
	def test_unsupported_native_cast(self, Sample):
		inst = Sample.from_mongo({'field': Document()})
		
		with pytest.raises(ValueError):
			inst.field
	
	def test_unsupported_foreign_cast(self, Sample):
		inst = Sample()
		
		with pytest.raises(ValueError):
			inst.field = Document()
