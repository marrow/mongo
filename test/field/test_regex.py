# encoding: utf-8

from __future__ import unicode_literals

from common import FieldExam
from marrow.mongo.field import Regex


class RegexField(FieldExam):
	__field__ = Regex
