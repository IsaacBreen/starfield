`starfield` allows you to define `attrs` classes with a single field that can be initialised using variadic-positional arguments (i.e. star `*`).

## Installation

To install `starfield`, run the following command in your terminal:

```bash
pip install starfield
```

## Usage

The following example shows how to use `starfield` to create a class that behaves like a list with some extra fields:

```python
from attrs import define, field
from starfield import starfield


@define(field_transformer=starfield)
class ShoppingList:
    items: list = field(init="*")
    store: str = field()


grocery_list = ShoppingList("Milk", "Bread", "Eggs", store="Supermarket")
```

Without `starfield`, you would have to explicitly pass a list to the initializer:

```python
from attrs import define, field


@define
class ShoppingList:
    items: list = field()
    store: str = field()


grocery_list = ShoppingList(["Milk", "Bread", "Eggs"], store="Supermarket")
```

## Why?

Nested fields can quickly become unwieldy when initializing objects with `attrs`. `attrs`'s documentation [explains](https://www.attrs.org/en/stable/init.html#) why it's usually better to use a `classmethod` than to modify the initializer.

> Passing complex objects into __init__ and then using them to derive data for the class unnecessarily couples your new class with the old class which makes it harder to test and also will cause problems later. 

> Generally speaking, the moment you think that you need finer control over how your class is instantiated than what attrs offers, it’s usually best to use a classmethod factory or to apply the builder pattern.

### Nested fields

To illustrate the power of `starfield`, let's look at a more complex example involving nested fields. Suppose we want to create a data structure to represent a simple grammatical expression:

```text
"I" ( "love" | "hate" ) ( "cats" | "dogs" )
```

We can define a class to represent this expression with `attrs` and `starfield`:

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

Without `starfield`, you would have to explicitly pass a list to the initializer:

```python
from attrs import define, field


@define
class And:
    children: list = field()


@define
class Or:
    children: list = field()


expr = And("I", [Or("love", "hate"), Or("cats", "dogs")])
```

## Notes

- `starfield` will make all non-star fields keyword-only.

- You can still set the star field using a keyword argument (e.g. `expr = And("I", items=[Or("love", "hate"), Or("cats", "dogs")])`).

- To make the string representation of the class more readable, `starfield` adds a `__rich_repr__` method to the class. However, this only works if you're using [rich](https://github.com/Textualize/rich) to stringify your objects. To add a `__repr__` method as well, you can pass `repr=True` to `starfield`.

## Limitations

- `starfield` only works with classes that use `attrs`.

- The behaviour of `starfield`'s `__repr__` method may be inconsistent with the [`attrs`-generated `__repr__` methods](https://github.com/python-attrs/attrs/blob/9fd0f82ff0d632136b95e1b8737b081e537aaaee/src/attr/_make.py#L1833) which are more complicated than one might expect.

## Related projects

- This feature has been [requested and discussed here](https://github.com/python-attrs/attrs/issues/110). The use of `init="*"` is also proposed. 

- [`pydantic`](https://docs.pydantic.dev/usage/models/#custom-root-types)'s root types serve a similar purpose. Notable, however, a class with a root type cannot have any other fields.

Please let me know if I've missed any.
