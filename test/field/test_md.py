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
