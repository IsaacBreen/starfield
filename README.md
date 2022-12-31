Lets you define `attrs` classes with a single non-keyword-only field that can be initialised using
var-positional (i.e. star `*`) arguments.

## Installation

```bash
pip install starfield
```

## Usage

```python
from attrs import define, field
from starfield import starfield


@define(field_transformer=starfield)
class SantaList:
    names: list = field(init="*")
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

`attrs`'s documentation [recommends](https://www.attrs.org/en/stable/init.html#) explains why it's usually better to use a `classmethod` than to
modify the initializer.

> Passing complex objects into __init__ and then using them to derive data for the class unnecessarily couples your new class with the old class which makes it harder to test and also will cause problems later.

> Generally speaking, the moment you think that you need finer control over how your class is instantiated than what attrs offers, it’s usually best to use a classmethod factory or to apply the builder pattern.



### Nested fields

To motivate `starfield` more strongly, let's look at a more complex example involving nested fields.

Suppose we want to create a data structure to represent a simple grammatical expression:

```text
"I" ( "love" | "hate" ) ( "cats" | "dogs" )
```

We can define a class to represent this expression with `attrs`:

```python
from attrs import define, field


@define
class And:
    children: list = field()


@define
class Or:
    children: list = field()


expr = And(["I", Or(["love", "hate"]), Or(["cats", "dogs"])])
```

This works but it's a bit awkward to have to manually pass the list at every level.

Using `starfield` we can define the same class but with a much simpler initializer:

```python
from attrs import define, field
from starfield import starfield


@define(field_transformer=starfield)
class And:
    children: list = field(init="*")


@define(field_transformer=starfield)
class Or:
    children: list = field(init="*")


expr = And("I", Or("love", "hate"), Or("cats", "dogs"))
```

## How?

The `starfield` adds to the class an `__init__` method that accepts variadic positional arguments.
The `__init__` method calls `__attrs_init__` with the variadic positional arguments passed as a tuple to the field with `init="*"`.

### String representation

To make the string representation of the class more readable, `starfield` also adds a `__rich_repr__` method to the class. However, this only works if you're using [rich](https://github.com/Textualize/rich) to stringify your objects.

To add a `__repr__` method as well, you can pass `repr=True` to `starfield`.
However, its behaviour may be inconsistent with the [`attrs`-generated `__repr__` methods](https://github.com/python-attrs/attrs/blob/9fd0f82ff0d632136b95e1b8737b081e537aaaee/src/attr/_make.py#L1833)
which are more complicated than one might expect (and may change without warning - hence why `starfield` doesn't touch it unless you explicitly ask it to).

## Notes

- `starfield` will make all non-star fields keyword-only.

- You can still set the star field using a keyword argument (e.g. `SantaList(names=["Bob", "Alice"], is_naughty_list=True)`).

## Similar projects

- This feature has been [requested and discussed here](https://github.com/python-attrs/attrs/issues/110). The use of `init="*"` is also proposed. 

- [`pydantic`](https://docs.pydantic.dev/usage/models/#custom-root-types)'s root types serve a similar purpose. Notable, however, a class with a root type cannot have any other fields.

Please let me know if I've missed any.