import pytest

from marrow.mongo import Document


class FieldExam(object):
	__args__ = tuple()
	__kwargs__ = dict()
	
	@pytest.fixture()
	def Sample(self, request):
		class Sample(Document):
			field = self.__field__(*self.__args__, **self.__kwargs__)
		
		return Sample
