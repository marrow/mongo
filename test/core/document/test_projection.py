# encoding: utf-8

from marrow.mongo import Document, Field
from marrow.mongo.trait import Collection


class NoProjection(Collection):
	id = None
	default = Field()


class OnlyProjected(Collection):
	id = None
	default = Field()
	always = Field(project=True)


class RejectOnly(Collection):
	id = None
	default = Field()
	never = Field(project=False)


class TestDocumentProjection(object):
	def test_no_projection(self):
		assert NoProjection.__projection__ is None
	
	def test_sample_projection(self):
		assert OnlyProjected.__projection__ == {'always': True}
	
	def test_reject_only_policy(object):
		assert RejectOnly.__projection__ == {'default': True}
