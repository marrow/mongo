from .string import String


class Regex(String):
	__foreign__ = 'regex'
	__disallowed_operators__ = {'#array'}
