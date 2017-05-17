# encoding: utf-8

from __future__ import unicode_literals

from .base import String
from ....schema.compat import unicode, py3

try:
	from pathlib import PurePosixPath as _Path
except ImportError:
	from pathlib2 import PurePosixPath as _Path


class Path(String):
	def to_native(self, obj, name, value):  # pylint:disable=unused-argument
		return _Path(value)
