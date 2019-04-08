"""Formalized types for use as annotations, e.g. with typeguard."""

from typing import Sequence
from typing import Tuple
from typing import Union

from typeguard import check_argument_types


__all__ = ['check_argument_types', 'Sort', 'FieldOrder']


# Representing the definition of sort order according to PyMongo.
Sort = Sequence[Tuple[str, int]]

# Parametric sort order is more permissive.
FieldOrder = Sequence[Union[str, Tuple[str, int]]]
