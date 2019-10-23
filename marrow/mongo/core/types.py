"""Formalized types for use as annotations, e.g. with typeguard."""

from collections import namedtuple

from typing import Any, Callable, Iterable, List, Mapping, Optional, Sequence, Tuple, Type, TypeVar, Union, Set

from typeguard import check_argument_types


__all__ = [
		'Any',
		'Callable',
		'FieldContext',
		'FieldType',
		'Iterable',
		'List',
		'Mapping',
		'OperationMap',
		'Optional',
		'Order',
		'Projection',
		'PushSort',
		'Sequence',
		'Set',
		'Sort',
		'Tuple',
		'Type',
		'TypeVar',
		'Union',
		'check_argument_types',
		'namedtuple',
	]


Projection = Mapping[str, bool]
Sort = Sequence[Union[str, Tuple[str, int]]]
PushSort = Union[int, Mapping[str, int]]
Order = Union[str, Tuple[str, int]]

OperationMap = Mapping[str, Callable]

FieldContext = namedtuple('FieldContext', 'field,document')
FieldType = TypeVar("FieldType", bound="Field")
