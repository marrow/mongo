# encoding: utf-8

from __future__ import unicode_literals

import pytest

from marrow.mongo import Document
from marrow.mongo.field import Markdown



class TestMarkdownField(object):
	class Sample(Document):
		text = Markdown()
	
	def test_plain_text(self):
		inst = self.Sample("This is a test.")
		assert inst.text == 'This is a test.'
	
	def test_formatted_text(self):
		inst = self.Sample("This is a **test**.")
		assert inst.text == 'This is a **test**.'
		assert inst.text.__html__() == '<p>This is a <strong>test</strong>.</p>\n'
	
	def test_default_code_block(self):
		inst = self.Sample('```\ndef hello(name):\n\tprint("Hello", name)\n```')
		result = inst.text.__html__()
		assert '<pre>' in result
		assert '<code>' in result
	
	def test_valid_code_block(self):
		inst = self.Sample('```python\ndef hello(name):\n\tprint("Hello", name)\n```')
		result = inst.text.__html__()
		assert '<pre>' in result
		assert 'language-python' in result
	
	def test_invalid_code_block(self):
		inst = self.Sample('```xyzzy\ndef hello(name):\n\tprint("Hello", name)\n```')
		result = inst.text.__html__()
		assert '<pre>' in result
		assert 'language-xyzzy' in result



	#def test_data_assignment(self):
	#	inst = self.Sample.from_mongo({'field': [{'field': 'foo'}]})
	#	inst.alias = 'bar'
	#	assert inst.__data__ == {'field': [{'field': 'bar'}]}
