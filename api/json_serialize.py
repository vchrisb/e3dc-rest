from datetime import datetime
from functools import singledispatch


@singledispatch
def to_serializable(val):
    """Used by default."""
    return str(val)


@to_serializable.register
def ts_datetime(val: datetime):
    """Used if *val* is an instance of datetime."""
    return val.isoformat()
