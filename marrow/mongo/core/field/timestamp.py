from .date import Date


class Timestamp(Date):
	__foreign__ = 'timestamp'
	__disallowed_operators__ = {'#array'}
