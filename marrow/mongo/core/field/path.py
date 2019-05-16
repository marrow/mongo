from .string import String

from pathlib import PurePosixPath as _Path


class Path(String):
	def to_native(self, obj, name:str, value:str) -> _Path:  # pylint:disable=unused-argument
		return _Path(value)
