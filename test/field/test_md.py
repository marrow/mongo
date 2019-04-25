from common import FieldExam
from marrow.mongo.field import Markdown


class TestMarkdownField(FieldExam):
	__field__ = Markdown
	
	def test_plain_text(self, Sample):
		inst = Sample("This is a test.")
		assert inst.field == 'This is a test.'
	
	def test_formatted_text(self, Sample):
		inst = Sample("This is a **test**.")
		assert inst.field == 'This is a **test**.'
		assert inst.field.__html__() == '<p>This is a <strong>test</strong>.</p>\n'
	
	def test_cast_protocol_magic(self, Sample):
		class Inner(object):
			def __markdown__(self):
				return "Some Markdown text."
		
		inst = Sample(Inner())
		assert inst.field == 'Some Markdown text.'
	
	def test_cast_protocol_property(self, Sample):
		class Inner(object):
			@property
			def as_markdown(self):
				return "Other Markdown text."
		
		inst = Sample(Inner())
		assert inst.field == 'Other Markdown text.'
