# Coding standards

## Type hinting

- Apply type hints to all function parameters and return values, including in unit test modules.
- Use modern type hinting. Example: Do not use Dict, List, Optional; use dict, list, | instead.

## Strings

- Use f-strings for string interpolation.

## Classes

Use dataclasses where applicable, in descending order of preference:
1. @attrs.frozen
2. @attrs.define (only where mutability is required)
3. @dataclass

Use kw_only=True except when there is only one argument.

## Keyword args

Use keyword-only arguments for functions with more than one argument.

## Formatting

Use trailing commas in function signatures or lists with more than two items, except where it would reduce readability.

## Tuple unpacking

Avoid tuple unpacking, except in trivial (at most two return values) or localized use cases. Prefer to define and return dataclasses with documented attributes.

## Docstrings

Follow the Google style guide for function docstrings.

## Conditionals

Reorder to avoid negation: prefer `result = foo if condition else bar` instead of `result = bar if not condition else foo`.
