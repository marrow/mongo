# encoding: utf-8

'''
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
		__import__('pudb').set_trace()
		
		inst = self.Sample.from_mongo({'locale': [
				{'language': 'en', 'word': 'hello'},
				{'language': 'fr', 'word': 'bonjour'}
			]})
		
		assert inst.word == {'en': 'hello', 'fr': 'bonjour'}


class TestLocalized(object):
	class Sample(Localized):
		class Locale(Localized.Locale):
			word = String()
		
		word = Translated('word')
	
	def test_repr(self):
		pass
'''
