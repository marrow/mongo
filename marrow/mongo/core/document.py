# encoding: utf-8

from collections import OrderedDict as odict, MutableMapping
from itertools import chain

from marrow.schema import Container, Attribute


class Document(Container):
	__foreign__ = 'object'
