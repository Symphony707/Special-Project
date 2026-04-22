import asyncio
import functools
from typing import Any, Callable, TypeVar

T = TypeVar("T")

async def run_agent_async(func: Callable[..., T], *args: Any, **kwargs: Any) -> T:
    """
    Executes a synchronous agent function in a separate thread to avoid blocking the event loop.
    """
    # Create a partial if there are kwargs as asyncio.to_thread only takes args
    if kwargs:
        return await asyncio.to_thread(functools.partial(func, *args, **kwargs))
    return await asyncio.to_thread(func, *args)

import json
import numpy as np

class ForensicEncoder(json.JSONEncoder):
    """Custom JSON encoder for NumPy types and other forensic data structures."""
    def default(self, obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj)
        if hasattr(obj, 'to_dict'):
            return obj.to_dict()
        return super().default(obj)

def serialize_agent_result(result: Any) -> Any:
    """Helper to ensure agent results are JSON serializable using ForensicEncoder."""
    return json.loads(json.dumps(result, cls=ForensicEncoder))

