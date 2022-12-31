from typing import List

from attrs import Attribute


def starfield(target_class: type, attributes: List[Attribute]) -> List[Attribute]:
    variadic_attributes = [attribute for attribute in attributes if attribute.init == "*"]
    if len(variadic_attributes) != 1:
        raise ValueError(
            f"Expected exactly one attribute with init='*', got {len(variadic_attributes)}: {variadic_attributes}"
        )
    variadic_attribute = attributes[0]

    def __init__(self, *args, **kwargs):
        if variadic_attribute.name in kwargs and len(args) > 0:
            raise ValueError(
                f"Cannot pass star field {variadic_attribute.name} as a keyword argument when there are variadic positional arguments"
            )
        kwargs[variadic_attribute.name] = args
        self.__attrs_init__(**kwargs)

    if hasattr(target_class, "__attrs_attrs__"):
        if not hasattr(target_class, "__attrs_init__"):
            target_class.__attrs_init__ = target_class.__init__
        target_class.__init__ = __init__
    else:
        target_class.__init__ = __init__

    return [
        attribute if attribute == variadic_attribute else attribute.evolve(kw_only=True)
        for attribute in attributes
    ]
