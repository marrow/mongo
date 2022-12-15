import pytest

from common import FieldExam
from marrow.mongo.field import Link


class TestLinkField(FieldExam):
	__field__ = Link
	
	def test_complete_url(self, Sample):
		uri = "http://user:pass@host:8088/path?query#fragment"
		inst = Sample(uri)
		assert inst['field'] == uri
		assert inst.field == uri
	
	def test_mailto(self, Sample):
		uri = "mailto:user@example.com"
		inst = Sample(uri)
		assert inst['field'] == uri
		assert inst.field == uri
	
	def test_urn(self, Sample):
		uri = "urn:ISBN0-486-27557-4"
		inst = Sample(uri)
		assert inst['field'] == uri
		assert inst.field == uri
	
	@pytest.mark.skip(reason="See: https://github.com/marrow/uri/issues/4")
	def test_protocol_relative(self, Sample):
		uri = "//example.com/protocol/relative"
		inst = Sample(uri)
		assert inst['field'] == uri
		assert inst.field == uri
	
	def test_host_relative(self, Sample):
		uri = "/host/relative"
		inst = Sample(uri)
		assert inst['field'] == uri
		assert inst.field == uri
	
	def test_context_relative(self, Sample):
		uri = "local/relative"
		inst = Sample(uri)
		assert inst['field'] == uri
		assert inst.field == uri
	
	def test_fragment_only(self, Sample):
		uri = "#fragment-only"
		inst = Sample(uri)
		assert inst['field'] == uri
		assert inst.field == uri


class TestLinkFieldAbsoluteSafety(FieldExam):
	__field__ = Link
	__kwargs__ = {'absolute': True}
	
	def test_complete_url(self, Sample):
		uri = "http://user:pass@host:8088/path?query#fragment"
		inst = Sample(uri)
		assert inst['field'] == uri
	
	def test_mailto(self, Sample):
		uri = "mailto:user@example.com"
		inst = Sample(uri)
		assert inst['field'] == uri
	
	def test_urn(self, Sample):
		uri = "urn:ISBN0-486-27557-4"
		inst = Sample(uri)
		assert inst['field'] == uri
	
	def test_protocol_relative(self, Sample):
		uri = "//example.com/protocol/relative"
		
		with pytest.raises(ValueError):
			Sample(uri)
	
	def test_host_relative(self, Sample):
		uri = "/host/relative"
		
		with pytest.raises(ValueError):
			Sample(uri)
	
	def test_context_relative(self, Sample):
		uri = "local/relative"
		
		with pytest.raises(ValueError):
			Sample(uri)
	
	def test_fragment_only(self, Sample):
		uri = "#fragment-only"
		
		with pytest.raises(ValueError):
			Sample(uri)


class TestLinkFieldProtocolSafety(FieldExam):
	__field__ = Link
	__kwargs__ = {'protocols': {'http', 'https'}}
	
	def test_complete_url(self, Sample):
		uri = "http://user:pass@host:8088/path?query#fragment"
		inst = Sample(uri)
		assert inst['field'] == uri
	
	def test_mailto(self, Sample):
		uri = "mailto:user@example.com"
		
		with pytest.raises(ValueError):
			Sample(uri)
	
	def test_urn(self, Sample):
		uri = "urn:ISBN0-486-27557-4"
		
		with pytest.raises(ValueError):
			Sample(uri)
	
	def test_protocol_relative(self, Sample):
		uri = "//example.com/protocol/relative"
		
		with pytest.raises(ValueError):
			Sample(uri)
	
	def test_host_relative(self, Sample):
		uri = "/host/relative"
		
		with pytest.raises(ValueError):
			Sample(uri)
	
	def test_context_relative(self, Sample):
		uri = "local/relative"
		
		with pytest.raises(ValueError):
			Sample(uri)
	
	def test_fragment_only(self, Sample):
		uri = "#fragment-only"
		
		with pytest.raises(ValueError):
			Sample(uri)
