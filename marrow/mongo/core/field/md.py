# encoding: utf-8

from __future__ import unicode_literals

from misaka import Markdown, HtmlRenderer  # , SmartyPants
from misaka import HTML_ESCAPE, HTML_HARD_WRAP
from misaka import EXT_FENCED_CODE, EXT_NO_INTRA_EMPHASIS, EXT_AUTOLINK, EXT_SPACE_HEADERS, EXT_STRIKETHROUGH, EXT_SUPERSCRIPT

from .base import String
from ....schema.compat import unicode, py3


md = Markdown(
		HtmlRenderer(flags=HTML_ESCAPE | HTML_HARD_WRAP),
		extensions = EXT_FENCED_CODE | \
				EXT_NO_INTRA_EMPHASIS | \
				EXT_AUTOLINK | \
				EXT_SPACE_HEADERS | \
				EXT_STRIKETHROUGH | \
				EXT_SUPERSCRIPT
	)


class MarkdownString(unicode):
	def __html__(self):
		return md(self)


class Markdown(String):
	def to_foreign(self, obj, name, value):  # pylint:disable=unused-argument
		if hasattr(value, '__markdown__'):
			return value.__markdown__()
		
		if hasattr(value, 'as_markdown'):
			return value.as_markdown
		
		return super(Markdown, self).to_foreign(obj, name, value)
	
	def to_native(self, obj, name, value):  # pylint:disable=unused-argument
		return MarkdownString(value)
