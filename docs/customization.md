# Error Customization

Hetman Pipeline provides flexible error customization through the `ERROR_TEMPLATES` system. You can customize error messages globally, per handler, or per handler mode.

---

## Understanding ERROR_TEMPLATES

Condition and match handlers have an `ERROR_TEMPLATES` class variable that defines error messages for different handler modes.

### Handler Modes

| Mode                  | Description                                    |
| --------------------- | ---------------------------------------------- |
| `HandlerMode.ROOT`    | Handler processes the value directly           |
| `HandlerMode.ITEM`    | Handler processes each item in a collection    |
| `HandlerMode.CONTEXT` | Handler uses a value from the pipeline context |

---

## Basic Error Template Structure

```python
from pipeline.handlers import HandlerMode, ConditionHandler

class Condition(ConditionHandler):
    ERROR_TEMPLATES = {
        HandlerMode.ROOT: lambda self: "Error message here"
    }
```

The lambda function receives `self` (the handler instance) and returns a error message any type.

---

## Customization Levels

### 1. Quick Assignment (Most Common)

Directly override the `ERROR_TEMPLATES` dictionary for a specific handler:

```python
from pipeline import Pipe
from pipeline.handlers import HandlerMode

# Customize the Email validator error message
Pipe.Match.Format.Email.ERROR_TEMPLATES[HandlerMode.ROOT] = lambda _: "Please provide a valid email address."

# Now use it
result = Pipe(
    value="invalid-email",
    type=str,
    matches={Pipe.Match.Format.Email: None}
).run()

print(result.match_errors)
# [{'id': 'email', 'msg': 'Please provide a valid email address.', 'value': 'invalid-email'}]
```

---

### 2. Dynamic Error Messages

Use handler properties to create dynamic error messages:

```python
from pipeline import Pipe
from pipeline.handlers import HandlerMode

# Customize MinLength to show the expected length
Pipe.Condition.MinLength.ERROR_TEMPLATES[HandlerMode.ROOT] = lambda self: (
    f"Value must be at least {self.argument} characters long."
)

result = Pipe(
    value="Hi",
    type=str,
    conditions={Pipe.Condition.MinLength: 10}
).run()

print(result.condition_errors)
# [{'id': 'min_length', 'msg': 'Value must be at least 10 characters long.', 'value': 'Hi'}]
```

---

### 3. Mode-Specific Customization

Customize error messages for different handler modes:

```python
from pipeline import Pipe
from pipeline.handlers import HandlerMode, Item

# Customize for both ROOT and ITEM modes
Pipe.Match.Format.Email.ERROR_TEMPLATES[HandlerMode.ROOT] = lambda _: "Invalid email address."
Pipe.Match.Format.Email.ERROR_TEMPLATES[HandlerMode.ITEM] = lambda self: f"Invalid email at position {self._item_index}."

# ROOT mode
result = Pipe(
    value="invalid",
    type=str,
    matches={Pipe.Match.Format.Email: None}
).run()

print(result.match_errors[0]['msg'])
# "Invalid email address."

# ITEM mode
result = Pipe(
    value=["valid@email.com", "invalid", "another@email.com"],
    type=list,
    matches={Item(Pipe.Match.Format.Email): None}
).run()

print(result.match_errors[0][1]['msg'])
# "Invalid email at position 1."
```

---

## Real-World Examples

### Example 1: Localized Error Messages

```python
from contextvars import ContextVar
from pipeline import Pipe
from pipeline.handlers import ConditionHandler, HandlerMode, ConditionFlag

locale = ContextVar("locale", default="en")

i18n = {
    "en": "Too short. This must be at least {argument} characters.",
    "pl": "Za krótkie. To musi mieć conajmniej {argument} znaków."
}

Pipe.Condition.MinLength.ERROR_TEMPLATES[HandlerMode.ROOT] = lambda self: (
    i18n.get(locale.get(), i18n["en"]).format(argument=self.argument)
)

# Test
result_en = Pipe(
    value="invalid",
    type=str,
    conditions={Pipe.Condition.MinLength: 100}
).run()

print(result_en.condition_errors)
# [{'id': 'min_length', 'msg': 'Too short. This must be at least 100 characters.', 'value': 'invalid'}]

locale.set("pl")

result_pl = Pipe(
    value="invalid",
    type=str,
    conditions={Pipe.Condition.MinLength: 100}
).run()

print(result_pl.condition_errors)
# [{'id': 'min_length', 'msg': 'Za krótkie. To musi mieć conajmniej 100 znaków.', 'value': 'invalid'}]
```

---

### Example 2: Context-Aware Error Messages

```python
from pipeline import Pipe
from pipeline.handlers import HandlerMode

# Customize to show both the value and the argument
Pipe.Condition.MinNumber.ERROR_TEMPLATES[HandlerMode.ROOT] = lambda self: (
    f"Value {self.value} is below the minimum of {self.argument}."
)

Pipe.Condition.MaxNumber.ERROR_TEMPLATES[HandlerMode.ROOT] = lambda self: (
    f"Value {self.value} exceeds the maximum of {self.argument}."
)

result = Pipe(
    value=5,
    type=int,
    conditions={
        Pipe.Condition.MinNumber: 10,
        Pipe.Condition.MaxNumber: 100
    }
).run()

print(result.condition_errors[0]['msg'])
# "Value 5 is below the minimum of 10."
```

---

## Advanced: Custom Error Builder

For complete control over the error structure, you can customize the `ERROR_BUILDER` function. This allows you to change not just the message, but the entire error object structure.

### Per-Handler Error Builder

```python
from pipeline import Pipe
from pipeline.handlers import HandlerMode

def custom_email_error_builder(handler):
    """Custom error builder with detailed information"""
    return {
        "field": handler.id,
        "message": "Invalid email format",
        "value": handler.value,
        "suggestion": "Email must be in format: user@domain.com",
        "examples": ["john@example.com", "jane.doe@company.org"]
    }

# Assign the custom builder to a specific handler
Pipe.Match.Format.Email.ERROR_BUILDER = custom_email_error_builder
```

### Global Error Builder

You can also change the `ERROR_BUILDER` globally for all condition or match handlers:

```python
from pipeline.handlers import ConditionHandler, MatchHandler

def global_condition_error_builder(handler):
    """Global error builder for all condition handlers"""
    return {
        "error_type": "validation_error",
        "handler": handler.id,
        "message": handler.error_msg,
        "value": handler.value,
        "timestamp": datetime.now()
    }

def global_match_error_builder(handler):
    """Global error builder for all match handlers"""
    return {
        "error_type": "format_error",
        "handler": handler.id,
        "message": handler.error_msg,
        "value": handler.value
    }

# Apply globally to all condition handlers
ConditionHandler.ERROR_BUILDER = global_condition_error_builder

# Apply globally to all match handlers
MatchHandler.ERROR_BUILDER = global_match_error_builder
```

!!! warning "Global vs Per-Handler"

    When you set `ERROR_BUILDER` on a base class (like `ConditionHandler`), it affects **all** handlers that inherit from it. Setting it on a specific handler (like `Pipe.Match.Format.Email`) only affects that handler.

---

## Accessing Handler Properties

Inside the error template lambda, you have access to all handler properties:

| Property           | Description                       |
| ------------------ | --------------------------------- |
| `self.value`       | The value being validated         |
| `self.argument`    | The handler's argument            |
| `self.id`          | Handler identifier (snake_case)   |
| `self._item_index` | Current item index (in ITEM mode) |
| `self.context`     | Pipeline context                  |
| `self.metadata`    | Pipe metadata                     |

---

## Best Practices

!!! tip "Keep Messages User-Friendly"

    Write error messages for end users, not developers:

    ```text
    # Bad
    lambda _: "Regex pattern mismatch"

    # Good
    lambda _: "Please enter a valid phone number (e.g., +1234567890)"
    ```

!!! tip "Include Expected Values"

    Help users understand what's expected:

    ```text
    lambda self: f"Must be between {self.argument} and 100 characters"
    ```

!!! warning "Don't Expose Sensitive Data"

    Be careful not to expose sensitive information in error messages:

    ```text
    # Bad - exposes password
    lambda self: f"Password '{self.value}' is too weak"

    # Good
    lambda self: "Password does not meet security requirements"
    ```

!!! note "Consistency Across Modes"

    If you customize `HandlerMode.ROOT`, consider customizing `HandlerMode.ITEM` too:

    ```text
    ERROR_TEMPLATES = {
        HandlerMode.ROOT: lambda _: "Invalid email address",
        HandlerMode.ITEM: lambda self: f"Invalid email at position {self._item_index}"
    }
    ```

---

## Resetting to Defaults

If you need to reset error messages to their defaults, you can reload the handler class or manually restore the original templates.

```python
# Save original before customizing
original_template = Pipe.Match.Format.Email.ERROR_TEMPLATES.copy()

# Customize
Pipe.Match.Format.Email.ERROR_TEMPLATES[HandlerMode.ROOT] = lambda _: "Custom message"

# Restore later
Pipe.Match.Format.Email.ERROR_TEMPLATES = original_template
```

---

## Next Steps

-   Learn about [Pipeline Hooks](hooks.md) for custom processing logic
-   Explore [Handler Modifiers](modifiers.md) for Item() and Context()
-   Check [Framework Integrations](integrations.md) for Falcon integration
