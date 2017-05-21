# encoding: utf-8

from __future__ import unicode_literals

from .date import Date


class Timestamp(Date):
	__foreign__ = 'timestamp'
	__disallowed_operators__ = {'#array'}
