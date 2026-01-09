# Handler Modifiers

Handler modifiers are powerful tools that change **how** and **where** a handler operates. They allow you to apply validation, matching, or transformation logic to items within collections or to values from the pipeline context.

---

## Available Modifiers

### `Item()` - Process Collection Items

Apply a handler to **each item** in a list or dictionary.

### `Context()` - Use Context Values

Use a value from the **pipeline context** as the handler's argument.

---

## The `Item()` Modifier

The `Item()` modifier transforms a handler to operate on each element of a collection (list or dict) instead of the collection itself.

::: pipeline.handlers.base_handler.handler_modifiers.Item

    options:
        show_root_heading: true
        heading_level: 3

---

### Example 1: Validate All Items in a List

```python
from pipeline import Pipe
from pipeline.handlers import Item

# Validate that all emails in a list are valid
result = Pipe(
    value=["john@example.com", "jane@example.com", "admin@company.org"],
    type=list,
    matches={
        Item(Pipe.Match.Format.Email): None
    }
).run()

print(result.value)
# ['john@example.com', 'jane@example.com', 'admin@company.org']

# If one email is invalid:
result = Pipe(
    value=["john@example.com", "invalid-email", "admin@company.org"],
    type=list,
    matches={
        Item(Pipe.Match.Format.Email): None
    }
).run()

print(result.match_errors)
# [{1: {'id': 'email', 'msg': 'Invalid email address format.', 'value': 'invalid-email'}}]
```

---

### Example 2: Transform All Items

```python
from pipeline import Pipe
from pipeline.handlers import Item

# Capitalize all strings in a list
result = Pipe(
    value=["hello", "world", "python"],
    type=list,
    transform={
        Item(Pipe.Transform.Capitalize): None
    }
).run()

print(result.value)
# ['Hello', 'World', 'Python']
```

---

### Example 3: Using `use_key` with Dictionaries

The `use_key` parameter allows you to validate or transform **dictionary keys** instead of values.

```python
from pipeline import Pipe
from pipeline.handlers import Item

# Validate that all dictionary keys match a pattern
data = {
    "user_name": "John",
    "user_email": "john@example.com",
    "user_age": 30
}

result = Pipe(
    value=data,
    type=dict,
    matches={
        # Validate that all keys start with "user_"
        Item(Pipe.Match.Regex.Search, use_key=True): r"^user_"
    }
).run()

print(result.match_errors)
# [] - all keys match the pattern

# With invalid keys:
data_invalid = {
    "user_name": "John",
    "email": "john@example.com",  # Missing "user_" prefix
    "age": 30  # Missing "user_" prefix
}

result = Pipe(
    value=data_invalid,
    type=dict,
    matches={
        Item(Pipe.Match.Regex.Search, use_key=True): r"^user_"
    }
).run()

print(result.match_errors)
# [
#     {
#         'email': {
#             'id': 'search',
#             'msg': 'Invalid value. Valid pattern for value is ^user_.',
#             'value': 'email'
#         },
#         'age': {
#             'id': 'search',
#             'msg': 'Invalid value. Valid pattern for value is ^user_.',
#             'value': 'age'
#         }
#     }
# ]
```

---

### Example 4: Using `only_consider` for Type Filtering

The `only_consider` parameter allows you to apply a handler **only to items of a specific type**.

```python
from pipeline import Pipe
from pipeline.handlers import Item

# Mixed-type list: only capitalize strings
result = Pipe(
    value=["hello", 123, "world", 456, "python"],
    type=list,
    transform={
        Item(Pipe.Transform.Multiply, only_consider=int): 10
    }
).run()

print(result.value)
# ['hello', 1230, 'world', 4560, 'python']
# Only numbers were multiplied.
```

!!! warning "Mixed Types"

    By default, `only_consider` is set to `None`, which means it will consider all acceptable types for the handler. If the item's type is not acceptable, it will be skipped without any error.

---

### Example 5: Complex Validation with Item()

```python
from pipeline import Pipeline, Pipe
from pipeline.handlers import Item

# Validate a list of user objects
user_list_pipeline = Pipeline(
    users={
        "type": list,
        "conditions": {
            Pipe.Condition.MinLength: 1,
            Pipe.Condition.MaxLength: 100
        },
        "matches": {
            # Each item must be a valid email
            Item(Pipe.Match.Format.Email): None
        }
    }
)

result = user_list_pipeline.run(data={
    "users": [
        "admin@company.com",
        "user1company.com",
        "user2@company.com"
    ]
})

print(result.errors)
# {
#     "users": [
#         {
#             1: {
#                 "id": "email",
#                 "msg": "Invalid email address format.",
#                 "value": "user1company.com",
#             }
#         }
#     ]
# }
```

---

## The `Context()` Modifier

The `Context()` modifier allows a handler to use a value from the **pipeline context** as its argument, enabling dynamic validation based on other fields.

::: pipeline.handlers.base_handler.handler_modifiers.Context

    options:
        show_root_heading: true
        heading_level: 3

---

### Example 1: Password Confirmation

Validate that a password confirmation field matches the original password:

```python
from pipeline import Pipeline, Pipe
from pipeline.handlers import Context

# Create a registration pipeline
registration_pipeline = Pipeline(
    password={
        "type": str,
        "matches": {
            Pipe.Match.Format.Password: Pipe.Match.Format.Password.STRICT
        }
    },
    password_confirm={
        "type": str,
        "conditions": {
            # Use the 'password' field from context as the comparison value
            Context(Pipe.Condition.MatchesField): "password"
        }
    }
)

# Valid case: passwords match
result = registration_pipeline.run(data={
    "password": "SecurePass123!",
    "password_confirm": "SecurePass123!"
})

print(result.errors)
# None - passwords match

# Invalid case: passwords don't match
result = registration_pipeline.run(data={
    "password": "SecurePass123!",
    "password_confirm": "DifferentPass456!"
})

print(result.errors)
# {'password_confirm': [{'id': 'matches_field', 'msg': 'This must match the password field.', 'value': 'DifferentPass456!'}]}
```

---

### Example 2: Dynamic Range Validation

Validate that a value is within a range defined by other fields:

```python
from pipeline import Pipeline, Pipe
from pipeline.handlers import Context

# Product pricing pipeline
pricing_pipeline = Pipeline(
    min_price={
        "type": int,
        "conditions": {Pipe.Condition.MinNumber: 0}
    },
    max_price={
        "type": int,
        "conditions": {Pipe.Condition.MinNumber: 0}
    },
    current_price={
        "type": int,
        "conditions": {
            # Use min_price from context
            Context(Pipe.Condition.MinNumber): "min_price",
            # Use max_price from context
            Context(Pipe.Condition.MaxNumber): "max_price"
        }
    }
)

# Valid case
result = pricing_pipeline.run(data={
    "min_price": 10,
    "max_price": 100,
    "current_price": 50
})

print(result.errors)
# None - current_price is within range

# Invalid case
result = pricing_pipeline.run(data={
    "min_price": 10,
    "max_price": 100,
    "current_price": 150  # Exceeds max_price
})

print(result.errors)
# {'current_price': [{'id': 'max_number', 'msg': 'Must be 100 or less.', 'value': 150}]}
```

---

## Advanced Example: Nested Validation

```python
from pipeline import Pipeline, Pipe
from pipeline.handlers import Item

# Validate a complex nested structure
team_pipeline = Pipeline(
    team_name={
        "type": str,
        "conditions": {Pipe.Condition.MaxLength: 50}
    },
    members={
        "type": list,
        "conditions": {
            Pipe.Condition.MinLength: 1,
            Pipe.Condition.MaxLength: 10,
            # Each member must be a valid email
            Item(Pipe.Match.Format.Email): None
        },
        "transform": {
            # Lowercase all emails
            Item(Pipe.Transform.Lowercase): None
        }
    }
)

result = team_pipeline.run(data={
    "team_name": "Engineering",
    "members": [
        "Alice@Company.com",
        "Bob@Company.com",
        "Charlie@Company.com"
    ]
})

print(result.processed_data)
# {
#     'team_name': 'Engineering',
#     'members': ['alice@company.com', 'bob@company.com', 'charlie@company.com']
# }
```

---

## Best Practices

!!! tip "When to Use Item()"

    - Validating all elements in a list or dictionary
    - Transforming collection items uniformly
    - Applying type-specific logic with `only_consider`
    - Validating dictionary keys with `use_key`

!!! tip "When to Use Context()"

    - Password confirmation fields
    - Dynamic range validation
    - Field interdependencies
    - Conditional validation based on other fields

!!! warning "Context Availability"

    The `Context()` modifier requires that the referenced field exists in the pipeline context. If the field is missing, a `HandlerModeMissingContextValue` exception will be raised.

!!! note "Error Reporting"

    When using `Item()`, errors include an `index` property indicating which item failed:

    ```text
    # For lists: index is an integer (0, 1, 2, ...)
    # For dicts: index is the key name
    ```

---

## Next Steps

-   Learn about [Pipeline Hooks](hooks.md) for pre/post processing
-   Explore [Error Customization](customization.md) for custom error messages
-   Check [Examples](examples.md) for more real-world use cases
