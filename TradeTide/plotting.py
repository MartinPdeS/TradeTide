"""Small Matplotlib helpers used by TradeTide's public plotting methods."""

from collections.abc import Callable
from functools import wraps
from typing import Any

import matplotlib.pyplot as plt


def pre_plot(nrows: int = 1, ncols: int = 1) -> Callable:
    """Create axes for a plotting method when the caller does not provide them."""

    def decorator(function: Callable) -> Callable:
        @wraps(function)
        def wrapped(self: Any, *args: Any, **kwargs: Any):
            show = kwargs.pop("show", True)
            tight_layout = kwargs.pop("tight_layout", True)
            axes = kwargs.pop("axes", kwargs.pop("ax", None))
            if axes is None:
                figure, axes = plt.subplots(nrows=nrows, ncols=ncols)
            else:
                figure = axes.flat[0].figure if hasattr(axes, "flat") else axes.figure

            function(self, *args, axes=axes, **kwargs)
            if tight_layout:
                figure.tight_layout()
            if show:
                plt.show()
            return figure

        return wrapped

    return decorator


def post_mpl_plot(function: Callable) -> Callable:
    """Apply standard ``show`` and ``tight_layout`` options to an existing figure."""

    @wraps(function)
    def wrapped(*args: Any, **kwargs: Any):
        show = kwargs.pop("show", True)
        tight_layout = kwargs.pop("tight_layout", True)
        figure = function(*args, **kwargs)
        if tight_layout:
            figure.tight_layout()
        if show:
            plt.show()
        return figure

    return wrapped
