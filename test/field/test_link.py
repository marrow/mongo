# encoding: utf-8

from __future__ import unicode_literals

import pytest

from common import FieldExam
from marrow.mongo.field import Link
from marrow.schema.compat import str, unicode


class TestURLString(object):
	def test_complete_url(self):
		uri = "http://user:pass@host:8088/path?query#fragment"
		link = Link.URI(uri)
		assert uri.encode('utf8') == bytes(link)
		assert uri == unicode(link)
		
		assert link.scheme == 'http'
		assert link.user == 'user'
		assert link.password == 'pass'
		assert link.host == 'host'
		assert link.port == 8088
		assert unicode(link.path) == '/path'
		assert link.query == 'query'
		assert link.fragment == 'fragment'
		assert link.qs == 'query'
		
		assert not link.relative
		
		assert repr(link) == "URI('" + uri.replace('pass', '') + "')"
		
		with pytest.raises(ValueError):
			link['query']
		
		with pytest.raises(ValueError):
			link['foo'] = '27'
		
		with pytest.raises(ValueError):
			del link['bar']
		
		with pytest.raises(ValueError):
			list(link)
		
		with pytest.raises(ValueError):
			len(link)
	
	def test_complete_url_link(self):
		uri = "http://user:pass@host:8088/path?query#fragment"
		link = Link.URI(uri)
		
		assert link.__html__() == '<a href="' + uri + '">host/path</a>'
	
	def test_complete_url_comparison(self):
		uri = "http://user:pass@host:8088/path?query#fragment"
		link = Link.URI(uri)
		
		assert link == uri
		assert uri == link
		
		assert uri != 'foo'
		assert 'foo' != uri
	
	def test_mailto(self):
		uri = "mailto:user@example.com"
		link = Link.URI(uri)
		assert uri.encode('utf8') == bytes(link)
		assert uri == unicode(link)
		
		assert link.scheme == 'mailto'
		assert link.path.name == 'user@example.com'
		assert link.qs == ''
	
	def test_urn(self):
		uri = "urn:ISBN0-486-27557-4"
		link = Link.URI(uri)
		assert uri.encode('utf8') == bytes(link)
		assert uri == unicode(link)
		
		assert link.scheme == 'urn'
		assert link.path.name == 'ISBN0-486-27557-4'
	
	def test_protocol_relative(self):
		uri = "//example.com/protocol/relative"
		link = Link.URI(uri)
		assert uri.encode('utf8') == bytes(link)
		assert uri == unicode(link)
		
		assert not link.scheme
		assert link.relative
	
	def test_host_relative(self):
		uri = "/host/relative"
		link = Link.URI(uri)
		assert uri.encode('utf8') == bytes(link)
		assert uri == unicode(link)
		
		assert not link.host
		assert link.relative
	
	def test_context_relative(self):
		uri = "local/relative"
		link = Link.URI(uri)
		assert uri.encode('utf8') == bytes(link)
		assert uri == unicode(link)
		
		assert link.relative
	
	def test_fragment_only(self):
		uri = "#fragment-only"
		link = Link.URI(uri)
		assert uri.encode('utf8') == bytes(link)
		assert uri == unicode(link)
		
		assert link.relative
	
	def test_url_query(self):
		uri = "https://example.com/?foo=27&bar=42"
		link = Link.URI(uri)
		assert uri.encode('utf8') == bytes(link)
		assert uri == unicode(link)
		assert link == uri
		assert uri == link
		assert link != "https://example.com/?foo=42&bar=27"
		assert len(link) == 2
		assert set(link) == {'foo', 'bar'}
		
		assert link.query == {'foo': '27', 'bar': '42'}
		
		with pytest.raises(KeyError):
			link['baz']
		
		assert link['foo'] == '27'
		assert link['bar'] == '42'
		
		link['diz'] = 'fnord'
		del link['foo']
		
		assert link.query == {'bar': '42', 'diz': 'fnord'}
		
		assert "https://example.com/?diz=fnord&bar=42" == link
		assert link == "https://example.com/?diz=fnord&bar=42"
		assert link.qs in ["diz=fnord&bar=42", "bar=42&diz=fnord"]
		
		link.query = (('a', 1), ('b', 2))
		assert link == "https://example.com/?a=1&b=2"
		
		link.query = {}
		assert unicode(link) == "https://example.com/"
		
		link.qs = "a=1&a=2"
		assert link.query == {'a': ['1', '2']}
		assert link == "https://example.com/?a=1&a=2"
		assert link.qs == "a=1&a=2"
	
	def test_keyword_construction(self):
		uri = "http://example.com/"
		link = Link.URI(scheme="http", host="example.com", path="/")
		assert link == uri
	
	def test_keyword_unknown(self):
		with pytest.raises(TypeError):
			Link.URI(unknown="Bob Dole")
	
	def test_linkification(self):
		class Address(object):
			__link__ = 'mailto:user@example.com'
		
		assert Link.URI(Address()) == Address.__link__
	
	def test_recast(self):
		uri = "http://user:pass@host:8088/path?query#fragment"
		link = Link.URI(uri)
		assert link == Link.URI(link)
	
	def test_relative_resolution(self):
		uri = "https://example.com/about/"
		link = Link.URI(uri)
		
		assert unicode(link.resolve('/')) == 'https://example.com/'
		assert unicode(link.resolve('us')) == 'https://example.com/about/us'
		assert unicode(link.resolve('../img/banner.jpeg')) == 'https://example.com/img/banner.jpeg'
		assert unicode(link.resolve('//cdn.example.com/asset')) == 'https://cdn.example.com/asset'


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
