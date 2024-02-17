from collections.abc import Mapping
from typing import Any


def nested_update(orig: Mapping[Any, Any], new: Mapping[Any, Any]) -> dict[Any, Any]:
    # Credit: https://stackoverflow.com/a/31861045
    orig = dict(orig)
    for key, val in dict(new).items():
        if isinstance(val, Mapping):
            tmp = nested_update(orig.get(key, {}), val)
            orig[key] = tmp
        elif isinstance(val, list):
            orig[key] = orig[key] + val
        else:
            orig[key] = new[key]
    return orig
