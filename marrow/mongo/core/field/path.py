from pathlib import PurePosixPath as _Path

from .string import String


class Path(String):
	def to_native(self, obj, name, value):  # pylint:disable=unused-argument
		return _Path(value)
