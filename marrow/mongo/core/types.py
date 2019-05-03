"""Formalized types for use as annotations, e.g. with typeguard."""

from collections import namedtuple

from typing import Any, Callable, Iterable, List, Mapping, Optional, Sequence, Tuple, Type, Union

from typeguard import check_argument_types


__all__ = [
		'Callable',
		'Iterable',
		'List',
		'Mapping',
		'OperationMap',
		'OperationalCandidate',
		'Optional',
		'Projection',
		'Sequence',
		'Sort',
		'PushSort',
		'Tuple',
		'Type',
		'Union',
		'check_argument_types',
		'namedtuple',
		'Any',
	]


Projection = Mapping[str, bool]
Sort = Sequence[Union[str, Tuple[str, int]]]
PushSort = Union[int, Mapping[str, int]]
Order = Union[str, Tuple[str, int]]


OperationMap = Mapping[str, Callable]
