Lets you define `attrs` classes with a single non-keyword-only field called the *root* that can be initialised using
var-positional arguments.

## Installation

```bash
pip install attrs-root
```

## Usage

```python
from attrs import define, field
from attrs_root import root, transform_root


@transform_root
@define
class SantaList:
    names: list = root()
    is_naughty_list: bool = field()


naughty_list = SantaList("Bob", "Alice", is_naughty_list=True)
```

## Why?

Sometimes you want to define a class that behaves like a list with some extra fields.
Without an initializer with var-positional arguments, you would have to explicitly pass a list to the initializer:

```python
from attrs import define, field


@define
class SantaList:
    names: list = field()
    is_naughty_list: bool = field()


naughty_list = SantaList(["Bob", "Alice"], is_naughty_list=True)
```

This can get messy, especially if you have lots of nested fields.

The `attrs` documentation [recommends](https://www.attrs.org/en/stable/init.html#) using a `classmethod` rather than
modifying the initializer.

> Passing complex objects into __init__ and then using them to derive data for the class unnecessarily couples your new class with the old class which makes it harder to test and also will cause problems later.
>
> ...[We] strongly discourage from patterns like:
> 
> ```python
> pt = Point(**row.attributes)
> ```
> which couples your classes to the database data model.

### Nested fields

To motivate `attrs-root` more strongly, let's look at a more complex example involving nested fields.

Suppose Santa is extra busy this year and is looking for a way to cut corners.
He decides that, rather than tracking the naughty/nice status of every child individually, he'll arrange children into an arbitrary hierarchy of groups (e.g. countries, cities, schools) and implement a point-based system.

Without `attrs-root`, maintaining this data structure would be tricky:

```python
from attrs import define, field


@define
class Child:
    name: str = field()
    points: int = field()


@define
class Group:
    children: list['Group', Child] = field()
    name: str = field()
    points: int = field()


def compute_nice_list(entity: Group | Child, inherited_points: int = 0) -> list[Child]:
        if isinstance(entity, Child):
            if entity.points + inherited_points > 0:
                return [entity]
            else:
                return []
        else:
            return [nice_child for child in entity.children for nice_child in compute_nice_list(child, inherited_points + entity.points)]

world = Group(
    [
        Group(
            [
                Group(
                    [
                        Group(
                            [
                                Child("Bob", points=5),
                                Child("Alice", points=13),
                            ],
                            name= "St Mary's Primary School",
                            points=-10,
                        ),
                    ],
                    name="Sydney",
                    points=-3,
                ),
                Group(
                    [
                        Group(
                            [
                                Child("Elizabeth", points=-11),
                                Child("Isaac", points=-1),
                            ],
                            points=1,
                            name="Carine Senior High School",
                        ),
                    ],
                    name="Perth",
                    points=8,
                ),
            ],
            name="Australia",
            points=-3,
        )
    ],
    name="Earth",
    points=-4,
)

nice_list = compute_nice_list(world) # [Child("Alice", points=13)]
```

To be fair, we could write `world` more compactly.

```python
world = Group([
    Group([
        Group([
            Group([
                Child("Bob", points=5),
                Child("Alice", points=13),
            ], name="St Mary's Primary School", points=-10),
        ], name="Sydney", points=-3),
        Group([
            Group([
                Child("Elizabeth", points=-11),
                Child("Isaac", points=-1),
            ], points=1, name="Carine Senior High School"),
        ], name="Perth", points=8),
    ], name="Australia", points=-3),
], name="Earth", points=-4)
```

But that's still not very readable.

Using `attrs-root` we can write the same data structure more naturally:

```python
from attrs_root import root, transform_root


@transform_root
@define
class Group:
    children: list['Group', Child] = root()
    name: str = field()
    points: int = field()

world = Group(
    Group(
        Group(
            Group(
                Child("Bob", points=5),
                Child("Alice", points=13),
            ),
            name= "St Mary's Primary School",
            points=-10,
        ),
        name="Sydney",
        points=-3,
    ),
    Group(
        Group(
            Child("Elizabeth", points=-11),
            Child("Isaac", points=-1),
        ),
        points=1,
        name="Carine Senior High School",
    ),
    name="Australia",
    points=-3,
)

nice_list = compute_nice_list(world) # [Child("Alice", points=13)]
```

Note that the nested fields are initialised as if they were positional arguments,
but this works because `attrs-root` converts the initializer to the equivalent keyword-only initializer.
## How?

The `root` decorator is a thin wrapper around `field` that adds a little piece of metadata to the field that helps `transform_root` identify it.

The `transform_root` decorator replaces the `__init__` method of the class with a new one that accepts variadic positional arguments.
The new `__init__` method calls the original `__init__` with the positional arguments passed as a tuple to `root` field.

### String representation

To make the string representation of the class more readable, `transform_root` also adds a `__rich_repr__` method to the class. However, this only works if you're using [rich](https://github.com/Textualize/rich) to stringify your objects.

To replace the `__repr__` method as well, you can pass `repr=True` to `transform_root`.
However, its behaviour may be inconsistent with the [`attrs`-generated `__repr__` methods](https://github.com/python-attrs/attrs/blob/9fd0f82ff0d632136b95e1b8737b081e537aaaee/src/attr/_make.py#L1833)
which are more complicated than one might expect (and may change without warning - hence why `attrs-root` doesn't touch it unless you explicitly ask it to).

## Notes

`attrs-root` will make all non-root fields keyword-only.

You can still set the root field using a keyword argument (e.g. `SantaList(names=["Bob", "Alice"], is_naughty_list=True)`). It's up to you.

## Similar projects

- [`pydantic`](https://docs.pydantic.dev/usage/models/#custom-root-types)'s root types serve a similar purpose. Notable, however, a class with a root type cannot have any other fields.

Please let me know if I've missed any.