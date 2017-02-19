# encoding: utf-8

from marrow.mongo import Document, Field
from marrow.mongo.util import adjust_attribute_sequence, utcnow


class TestSequenceAdjustment(object):
	def test_default_punt(self):
		@adjust_attribute_sequence('last')
		class Inner(Document):
			last = Field()
			first = Field()
		
		assert Inner('first', 'last').first == 'first'
	
	def test_promotion(self):
		@adjust_attribute_sequence(-2, 'first')
		class Inner(Document):
			last = Field()
			first = Field()
		
		assert Inner('first', 'last').first == 'first'
