"""Composable helpers for combining indicator regions into trade signals."""

from collections.abc import Iterable

import numpy as np


def _normalise(regions: Iterable[Iterable[int]]) -> np.ndarray:
    values = np.asarray(list(regions), dtype=int)
    if values.ndim != 2 or values.shape[0] == 0:
        raise ValueError("regions must contain one or more equally sized signal sequences.")
    if not np.isin(values, (-1, 0, 1)).all():
        raise ValueError("signal values must be -1, 0, or 1.")
    return values


def all_of(*regions: Iterable[int]) -> np.ndarray:
    """Signal only where every input agrees on a buy or sell decision."""
    values = _normalise(regions)
    result = np.zeros(values.shape[1], dtype=int)
    result[np.all(values == 1, axis=0)] = 1
    result[np.all(values == -1, axis=0)] = -1
    return result


def any_of(*regions: Iterable[int]) -> np.ndarray:
    """Signal where all non-neutral inputs agree and at least one is non-neutral."""
    values = _normalise(regions)
    result = np.zeros(values.shape[1], dtype=int)
    result[np.any(values == 1, axis=0) & ~np.any(values == -1, axis=0)] = 1
    result[np.any(values == -1, axis=0) & ~np.any(values == 1, axis=0)] = -1
    return result


def weighted(*regions: Iterable[int], weights: Iterable[float], threshold: float = 0.0) -> np.ndarray:
    """Combine signals by weighted vote, returning neutral on a tie."""
    values = _normalise(regions)
    vote_weights = np.asarray(list(weights), dtype=float)
    if vote_weights.shape != (values.shape[0],):
        raise ValueError("weights must contain exactly one value per signal sequence.")
    if threshold < 0:
        raise ValueError("threshold must be non-negative.")
    scores = vote_weights @ values
    return np.where(
        scores > threshold,
        1,
        np.where(scores < -threshold, -1, 0),
    ).astype(int)
