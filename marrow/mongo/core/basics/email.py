# encoding: utf-8

from ... import Document
from ...field import String, Boolean, Date


__all__ = ('VerifiedAddress')


class VerifiedAddress(Document):
	__pk__ = 'address'
	
	address = String()
	primary = Boolean(default=False)
	
	added = Date(assign=True)
	verified = Date(default=None)
