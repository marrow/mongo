import pytest

from marrow.mongo import Document, Field
from marrow.mongo.util import adjust_attribute_sequence, utcnow


def test_utcnow():
	now = utcnow()
	assert now.tzinfo


class TestSequenceAdjustment:
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
	
	def test_explosion(self):
		with pytest.raises(TypeError):
			class Inner(Document):
				field = Field()
			
			@adjust_attribute_sequence('field')
			class Other(Inner):
				pass
