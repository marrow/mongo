# encoding: utf-8

from copy import deepcopy
from itertools import chain

from marrow.schema import Container, Attribute


class Document(Container):
	__foreign__ = 'object'

	