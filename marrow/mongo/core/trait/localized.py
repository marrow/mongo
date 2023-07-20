from collections import OrderedDict as odict

from ... import Document
from ...field import String, Mapping, Embed, Alias
from ....package import name
from ....package.loader import traverse


LANGUAGES = {'en', 'fr', 'it', 'de', 'es', 'pt', 'ru'}  # EFIGSPR, ISO 639-1
LANGUAGES |= {'da', 'nl', 'fi', 'hu', 'nb', 'pt', 'ro', 'sv', 'tr'}  # Additional ISO 639-1
LANGUAGES |= {'ara', 'prs', 'pes', 'urd'}  # ISO 636-3
LANGUAGES |= {'zhs', 'zht'}  # RLP


class Translated(Alias):
	"""Reference a localized field, providing a mapping interface to the translations.
	
		class MyDocument(Localized, Document):
			class Locale(Localized.Locale):
				title = String()
			
			title = Translated('title')
		
		# Query
		MyDocument.title == "Hello world!"
		
		inst = MyDocument([Locale('en', "Hi."), Locale('fr', "Bonjour.")])
		assert inst.title == {'en': "Hi.", 'fr': "Bonjour."}
	"""
	
	def __init__(self, path, **kw):
		super(Translated, self).__init__(path='locale.' + path, **kw)
	
	def __get__(self, obj, cls=None):
		if obj is None:
			return super(Translated, self).__get__(obj, cls)
		
		collection = odict()
		path = self.path[7:]
		
		for lang, locale in obj.locale.items():
			collection[lang] = traverse(locale, path)
		
		return collection
	
	def __set__(self, obj, value):
		raise TypeError("Can not assign to a translated alias.")  # TODO


class Localized(Document):
	"""The annotated Document contains localized data."""
	
	class Locale(Document):
		__pk__ = 'language'
		
		language = String(choices=LANGUAGES, default='en')
		
		def __repr__(self):
			return f"{name(self.__class__)}('{self.language}': {', '.join(set(self.__fields__) - {'language'})})"
	
	locale = Mapping('.Locale', key='language', default=lambda: [], assign=True, repr=False, positional=False)
	
	def __repr__(self):
		if self.locale:
			return super(Localized, self).__repr__('{' + ', '.join(self.locale) + '}')
		
		return super(Localized, self).__repr__()
