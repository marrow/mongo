from .string import String

try:
	from pathlib import PurePosixPath as _Path
except ImportError:
	from pathlib2 import PurePosixPath as _Path


class Path(String):
	def to_native(self, obj, name:str, value:str) -> _Path:  # pylint:disable=unused-argument
		return _Path(value)
