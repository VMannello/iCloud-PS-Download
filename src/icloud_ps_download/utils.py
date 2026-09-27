"""Utility helpers."""

from __future__ import annotations

from collections.abc import Iterable


def do_batch[T](value: Iterable[T], batch_size: int) -> Iterable[list[T]]:
    """Yield successive batches of *batch_size* items from *value*."""
    tmp: list[T] = []
    for item in value:
        if len(tmp) == batch_size:
            yield tmp
            tmp = []
        tmp.append(item)
    if tmp:
        yield tmp
