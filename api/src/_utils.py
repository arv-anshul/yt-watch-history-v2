from __future__ import annotations

from itertools import islice
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Iterable


def batch_iter(__l: list, __n: int, /) -> Iterable:
    """
    Iterator function that batches items from an iterator.

    Args:
        iterator (list): An iterator to be batched.
        n (int): The number of items per batch.

    Yields:
        A list of n items from the iterator, or the remaining items if there are less than n.
    """
    yield from (list(islice(__l, i, i + __n)) for i in range(0, len(__l), __n))
