# encoding: utf-8

from __future__ import unicode_literals

from .string import String


class Regex(String):
	__foreign__ = 'regex'
	__disallowed_operators__ = {'#array'}
