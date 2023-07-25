# encoding: utf-8

from __future__ import unicode_literals

from typing import MutableMapping

from common import FieldExam
from marrow.mongo import Document
from marrow.mongo.field import Mapping, String


class E(Document):
	name = String()
	value = String()


class TestMappingField(FieldExam):
	__field__ = Mapping
	__args__ = (E, )
	__kwargs__ = {'assign': True}
	
	def test_native_cast(self, Sample):
		inst = Sample.from_mongo({'field': [{'name': 'en', 'value': 'hello'},
				{'name': 'fr', 'value': 'bonjour'}]})
		
		mapping = inst.field
		assert isinstance(mapping, MutableMapping)
		assert 'en' in mapping
		assert isinstance(mapping['en'], E)
		assert mapping['fr'].value == 'bonjour'
	
	def test_foreign_cast(self, Sample):
		inst = Sample([E('en', 'hello')])
		
		mapping = inst.field
		mapping['fr'] = E('fr', 'bonjour')
		
		inst.field = mapping
		
		assert inst.__data__['field'] == [{'name': 'en', 'value': 'hello'},
				{'name': 'fr', 'value': 'bonjour'}]
