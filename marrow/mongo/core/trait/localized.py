# encoding: utf-8

from ... import Document
from ...field import String, Array, Embed


LANGUAGES = {'en', 'fr', 'it', 'de', 'es', 'pt', 'ru'}  # EFIGSPR, ISO 639-1
LANGUAGES |= {'da', 'nl', 'fi', 'hu', 'nb', 'pt', 'ro', 'sv', 'tr'}  # Additional ISO 639-1
LANGUAGES |= {'ara', 'prs', 'pes', 'urd'}  # ISO 636-3
LANGUAGES |= {'zhs', 'zht'}  # RLP


class Localized(Document):
	"""The annotated Document contains localized data."""
	
	class Locale(Document):
		__pk__ = 'language'
		
		language = String(choices=LANGUAGES, default='en')
	
	locale = Array(Embed(), default=lambda: [], assign=True, repr=False)
	
	def __repr__(self):
		if self.locale:
			return super(Localized, self).__repr__('{' + ', '.join(i.language for i in self.locale) + '}')
		
		return super(Localized, self).__repr__()
