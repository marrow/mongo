# encoding: utf-8

from __future__ import unicode_literals

import pytest

from marrow.mongo.field import String, Translated
from marrow.mongo.trait import Localized


class TestTranslated(object):
	class Sample(Localized):
		class Locale(Localized.Locale):
			word = String()
		
		word = Translated('word')
	
	def test_construction(self):
		inst = self.Sample.from_mongo({'locale': [
				{'language': 'en', 'word': 'hello'},
				{'language': 'fr', 'word': 'bonjour'}
			]})
		
		assert inst.word == {'en': 'hello', 'fr': 'bonjour'}
	
	def test_assignment(self):
		inst = self.Sample()
		
		with pytest.raises(TypeError):
			inst.word = None
	
	def test_query_translated(self):
		q = self.Sample.word == 'bonjour'
		assert q == {'locale.word': 'bonjour'}


class TestLocalized(object):
	class Sample(Localized):
		class Locale(Localized.Locale):
			word = String()
	
	def test_repr(self):
		inst = self.Sample.from_mongo({'locale': [
				{'language': 'en', 'word': 'hello'},
				{'language': 'fr', 'word': 'bonjour'}
			]})
		
		assert repr(inst) == "Sample({en, fr})"
	
	def test_empty_repr(self):
		inst = self.Sample()
		
		assert repr(inst) == "Sample()"
	
	def test_query(self):
		q = self.Sample.locale.word == 'bonjour'
		assert q == {'locale.word': 'bonjour'}
