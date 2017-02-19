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
	
	def test_cast_protocol_magic(self):
		class Inner(object):
			def __markdown__(self):
				return "Some Markdown text."
		
		inst = self.Sample(Inner())
		assert inst.text == 'Some Markdown text.'
	
	def test_cast_protocol_property(self):
		class Inner(object):
			@property
			def as_markdown(self):
				return "Other Markdown text."
		
		inst = self.Sample(Inner())
		assert inst.text == 'Other Markdown text.'
