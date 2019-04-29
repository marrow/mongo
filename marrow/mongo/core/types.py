"""Formalized types for use as annotations, e.g. with typeguard."""

from collections import namedtuple

from typing import Any, Callable, Iterable, List, Mapping, Optional, Sequence, Tuple, Type, Union, Mapping

from typeguard import check_argument_types


__all__ = [
		'Callable',
		'Iterable',
		'List',
		'Mapping',
		'OperationMap',
		'OperationalCandidate',
		'Optional',
		'Order',
		'Projection',
		'Sequence',
		'Sort',
		'Tuple',
		'Type',
		'Union',
		'check_argument_types',
		'namedtuple',
	]


Projection = Mapping[str, bool]
Sort = Sequence[Tuple[str, int]]
Order = Union[str, Tuple[str, int]]
PushOrder = Union[int, Mapping[str, int]]


OperationMap = Mapping[str, Callable]
