# encoding: utf-8

from __future__ import unicode_literals

from misaka import Markdown, HtmlRenderer  # , SmartyPants
from misaka import HTML_ESCAPE, HTML_HARD_WRAP
from misaka import EXT_FENCED_CODE, EXT_NO_INTRA_EMPHASIS, EXT_AUTOLINK, EXT_SPACE_HEADERS, EXT_STRIKETHROUGH, EXT_SUPERSCRIPT
from pygments import highlight, lexers, formatters
from pygments.lexers import get_lexer_by_name
from pygments.formatters import HtmlFormatter

from .base import String
from ....schema.compat import unicode, py3


class SourceRenderer(HtmlRenderer):  # , SmartyPants):
	_formatter = HtmlFormatter()
	
	def block_code(self, text, lang):
		s = ''
		
		if not lang:
			lang = 'text'
		
		try:
			lexer = get_lexer_by_name(lang, stripall=True)
		except:
			lexer = get_lexer_by_name('text', stripall=True)
		
		return highlight(text, lexer, self._formatter)


renderer = SourceRenderer(flags=HTML_ESCAPE | HTML_HARD_WRAP)
md = Markdown(renderer, extensions=EXT_FENCED_CODE | EXT_NO_INTRA_EMPHASIS | EXT_AUTOLINK | EXT_SPACE_HEADERS | \
		EXT_STRIKETHROUGH | EXT_SUPERSCRIPT)


class MarkdownString(unicode):
	def __html__(self):
		md.render(self)


class Markdown(String):
	def to_native(self, obj, name, value):  # pylint:disable=unused-argument
		return MarkdownString(value)
