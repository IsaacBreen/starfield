"""
An attrs field that absorbs positional arguments passed to the class constructor.
"""

from typing import *
from attrs import field
from delegatefn import delegate


@delegate(field, ignore=["init", "default"])
def root(**kwargs: Any) -> Any:
    """
    An attrs field that absorbs positional arguments passed to the class constructor and stores them in the field.
    """
    return field(**kwargs)