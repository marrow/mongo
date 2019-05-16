from pytest import raises

from marrow.mongo import Document, document, field, trait


class TestRegistryBehaviour:
	def test_registry_namespaces(self):
		assert document._namespace == 'marrow.mongo.document'
		assert field._namespace == 'marrow.mongo.field'
		assert trait._namespace == 'marrow.mongo.trait'
	
	def test_plugin_existence_check(self):
		assert 'Document' in document
		assert 'XYZZY' not in document
		assert 'Field' in field
		assert 'String' in field
		assert 'Bob' not in field
		assert 'Identified' in trait
		assert 'Localized' in trait
		assert 'Explosive' not in trait
	
	def test_registry_directory(self):
		plugins = dir(document)
		assert len(plugins) >= 1
		assert 'Document' in plugins  # A plugin.
		assert '__path__' in plugins  # Not a plugin, but a valid attribute.
	
	def test_protections(self):
		assert '_protected' not in document
		
		with raises(AttributeError):
			document._protected
		
		with raises(IndexError):
			document['_protected']
