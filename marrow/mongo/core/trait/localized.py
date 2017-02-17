# encoding: utf-8

from ... import Document
from ...field import String, Array, Embed


LANGUAGES = {'en', 'fr', 'it', 'de', 'es', 'pt', 'ru'}  # EFIGSPR, ISO 639-1
LANGUAGES |= {'da', 'nl', 'fi', 'hu', 'nb', 'pt', 'ro', 'sv', 'tr'}  # Additional ISO 639-1
LANGUAGES |= {'ara', 'prs', 'pes', 'urd'}  # ISO 636-3
LANGUAGES |= {'zhs', 'zht'}  # RLP


class Localized(Document):
	class Locale(Document):
		language = String(choices=LANGUAGES, default='en')
	
	locale = Array(Embed(), default=lambda: [], assign=True)
