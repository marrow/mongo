from common import FieldExam
from marrow.mongo.field import String


class TestStringField(FieldExam):
	__field__ = String
	
	def test_strip_basic(self, Sample):
		Sample.field.strip = True
		
		inst = Sample('\tTest\n   ')
		assert inst.field == 'Test'
	
	def test_strip_specific(self, Sample):
		Sample.field.strip = '* '
		
		inst = Sample('** Test *')
		assert inst.field == 'Test'
	
	def test_case_lower(self, Sample):
		Sample.field.case = 'lower'
		
		inst = Sample('Test')
		assert inst.field == 'test'
	
	def test_case_upper(self, Sample):
		Sample.field.case = 'upper'
		
		inst = Sample('Test')
		assert inst.field == 'TEST'
	
	def test_case_title(self, Sample):
		Sample.field.case = 'title'
		
		inst = Sample('Test words')
		assert inst.field == 'Test Words'
