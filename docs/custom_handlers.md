# Creating Custom Handlers

This guide shows you how to create your own custom `ConditionHandler`, `MatchHandler`, and `TransformHandler` to extend Hetman Pipeline with your specific business logic.

---

## Custom Condition Handlers

Condition handlers validate data integrity. They must implement the `query()` method that returns `True` if the condition passes, `False` otherwise.

### Basic Structure

```python
from pipeline.handlers.base_handler.resources.constants import HandlerMode
from pipeline.handlers.condition_handler.condition_handler import ConditionHandler

class MyCustomCondition(ConditionHandler[ValueType, ArgumentType]):
    """Your custom condition handler"""

    # Define which modes are supported
    SUPPORT = (HandlerMode.ROOT, HandlerMode.ITEM)

    # Define error messages for each mode
    ERROR_TEMPLATES = {
        HandlerMode.ROOT: lambda self: "Your error message here"
    }

    def query(self) -> bool:
        """
        Implement your validation logic here.

        Returns:
            True if validation passes, False otherwise
        """
        # Access self.value (the value being validated)
        # Access self.argument (the argument passed to the handler)
        return True  # Your logic here
```

### Example 1: Custom Age Validator

```python
from pipeline.handlers.base_handler.resources.constants import HandlerMode
from pipeline.handlers.condition_handler.condition_handler import ConditionHandler
from pipeline.core.pipe.pipe import Pipe

class IsAdult(ConditionHandler[int, None]):
    """Validates that age is 18 or older"""

    SUPPORT = (HandlerMode.ROOT, HandlerMode.ITEM)

    ERROR_TEMPLATES = {
        HandlerMode.ROOT: lambda self: f"Must be 18 or older. You are {self.value} years old."
    }

    def query(self) -> bool:
        return self.value >= 18

# Register it with Pipe
Pipe.Condition.IsAdult = IsAdult

# Use it
result = Pipe(
    value=16,
    type=int,
    conditions={Pipe.Condition.IsAdult: None}
).run()

print(result.condition_errors)
# [{'id': 'is_adult', 'msg': 'Must be 18 or older. You are 16 years old.', 'value': 16}]
```

### Example 2: Custom Business Rule

```python
from pipeline.handlers.base_handler.resources.constants import HandlerMode
from pipeline.handlers.condition_handler.condition_handler import ConditionHandler
from pipeline.core.pipe.pipe import Pipe

class IsValidCouponCode(ConditionHandler[str, list]):
    """Validates coupon code against a list of valid codes"""

    SUPPORT = (HandlerMode.ROOT,)

    ERROR_TEMPLATES = {
        HandlerMode.ROOT: lambda self: f"Invalid coupon code. Valid codes: {', '.join(self.argument[:3])}..."
    }

    def query(self) -> bool:
        # self.value is the coupon code
        # self.argument is the list of valid codes
        return self.value.upper() in [code.upper() for code in self.argument]

# Register and use
Pipe.Condition.IsValidCouponCode = IsValidCouponCode

valid_codes = ["SUMMER2024", "WELCOME10", "FREESHIP"]

result = Pipe(
    value="INVALID",
    type=str,
    conditions={Pipe.Condition.IsValidCouponCode: valid_codes}
).run()

print(result.condition_errors)
# [{'id': 'is_valid_coupon_code', 'msg': 'Invalid coupon code. Valid codes: SUMMER2024, WELCOME10, FREESHIP...', 'value': 'INVALID'}]
```

### Example 3: Context-Aware Validation

```python
from pipeline.handlers.base_handler.resources.constants import HandlerMode
from pipeline.handlers.condition_handler.condition_handler import ConditionHandler
from pipeline.core.pipeline.pipeline import Pipeline
from pipeline.core.pipe.pipe import Pipe
from pipeline.handlers.base_handler.handler_modifiers import Context

class IsGreaterThanField(ConditionHandler[int | float, int | float]):
    """Validates that value is greater than another field in context"""

    SUPPORT = (HandlerMode.CONTEXT,)

    ERROR_TEMPLATES = {
        HandlerMode.CONTEXT: lambda self: f"Must be greater than {self.input_argument} ({self.argument})"
    }

    def query(self) -> bool:
        return self.value > self.argument

# Register
Pipe.Condition.IsGreaterThanField = IsGreaterThanField

# Use in pipeline
pipeline = Pipeline(
    min_price={"type": int},
    max_price={
        "type": int,
        "conditions": {
            Context(Pipe.Condition.IsGreaterThanField): "min_price"
        }
    }
)

result = pipeline.run(data={
    "min_price": 100,
    "max_price": 50  # Invalid: should be > 100
})

print(result.errors)
# {'max_price': [{'id': 'is_greater_than_field', 'msg': 'Must be greater than min_price (100)', 'value': 50}]}
```

---

## Custom Match Handlers

Match handlers extend `ConditionHandler` and typically use regex patterns. They inherit the `search()` and `fullmatch()` helper methods.

---

## Custom Transform Handlers

Transform handlers modify values. They must implement the `operation()` method that returns the transformed value.

### Basic Structure

```python
from pipeline.handlers.base_handler.resources.constants import HandlerMode
from pipeline.handlers.transform_handler.transform_handler import TransformHandler

class MyCustomTransform(TransformHandler[ValueType, ArgumentType]):
    """Your custom transform handler"""

    SUPPORT = (HandlerMode.ROOT, HandlerMode.ITEM)

    def operation(self) -> ValueType:
        """
        Implement your transformation logic here.

        Returns:
            The transformed value
        """
        # Access self.value (the value to transform)
        # Access self.argument (the argument passed to the handler)
        return self.value  # Your transformation here
```

### Example 1: Custom String Sanitizer

```python
from pipeline.handlers.base_handler.resources.constants import HandlerMode
from pipeline.handlers.transform_handler.transform_handler import TransformHandler
from pipeline.core.pipe.pipe import Pipe
import re

class RemoveSpecialChars(TransformHandler[str, None]):
    """Removes all special characters, keeping only letters, numbers, and spaces"""

    SUPPORT = (HandlerMode.ROOT, HandlerMode.ITEM)

    def operation(self) -> str:
        return re.sub(r'[^a-zA-Z0-9\s]', '', self.value)

# Register
Pipe.Transform.RemoveSpecialChars = RemoveSpecialChars

# Use
result = Pipe(
    value="Hello! @World# 2024$",
    type=str,
    transform={Pipe.Transform.RemoveSpecialChars: None}
).run()

print(result.value)  # "Hello World 2024"
```

### Example 2: Custom Price Formatter

```python
from pipeline.handlers.base_handler.resources.constants import HandlerMode
from pipeline.handlers.transform_handler.transform_handler import TransformHandler
from pipeline.core.pipe.pipe import Pipe

class RoundToDecimalPlaces(TransformHandler[float, int]):
    """Rounds a float to specified decimal places"""

    SUPPORT = (HandlerMode.ROOT, HandlerMode.ITEM)

    def operation(self) -> float:
        # self.argument is the number of decimal places
        return round(self.value, self.argument)

# Register
Pipe.Transform.RoundToDecimalPlaces = RoundToDecimalPlaces

# Use
result = Pipe(
    value=19.99567,
    type=float,
    transform={Pipe.Transform.RoundToDecimalPlaces: 2}
).run()

print(result.value)  # 20.0
```

### Example 3: Custom List Transformer

```python
from pipeline.handlers.base_handler.resources.constants import HandlerMode
from pipeline.handlers.transform_handler.transform_handler import TransformHandler
from pipeline.core.pipe.pipe import Pipe

class SortList(TransformHandler[list, bool]):
    """Sorts a list. Argument: True for ascending, False for descending"""

    SUPPORT = (HandlerMode.ROOT,)

    def operation(self) -> list:
        return sorted(self.value, reverse=not self.argument)

# Register
Pipe.Transform.SortList = SortList

# Use
result = Pipe(
    value=[5, 2, 8, 1, 9],
    type=list,
    transform={Pipe.Transform.SortList: True}  # Ascending
).run()

print(result.value)  # [1, 2, 5, 8, 9]
```

### Example 4: Custom Data Masking

```python
from pipeline.handlers.base_handler.resources.constants import HandlerMode
from pipeline.handlers.transform_handler.transform_handler import TransformHandler
from pipeline.core.pipe.pipe import Pipe

class MaskCreditCard(TransformHandler[str, None]):
    """Masks credit card number, showing only last 4 digits"""

    SUPPORT = (HandlerMode.ROOT, HandlerMode.ITEM)

    def operation(self) -> str:
        # Remove spaces and dashes
        clean = self.value.replace(" ", "").replace("-", "")

        # Mask all but last 4 digits
        if len(clean) >= 4:
            return "*" * (len(clean) - 4) + clean[-4:]
        return clean

# Register
Pipe.Transform.MaskCreditCard = MaskCreditCard

# Use
result = Pipe(
    value="1234-5678-9012-3456",
    type=str,
    transform={Pipe.Transform.MaskCreditCard: None}
).run()

print(result.value)  # "************3456"
```

---

## Best Practices

!!! tip "Type Hints"

    Use proper type hints for `ValueType` and `ArgumentType`:

    ```python
    class MyHandler(ConditionHandler[str, int]):
        # str = value type
        # int = argument type
    ```

    !!! tip "Type Safety"

        Hetman Pipeline ensures type safety by validating the value and argument type before running the handler.

    !!! warning "Nested Types"

        Nested types like `list[str]` are not supported and any other nested types are not supported. Use `list` instead.

!!! tip "Support Multiple Modes"

    If your handler can work with collections, support `HandlerMode.ITEM`:

    ```python
    SUPPORT = (HandlerMode.ROOT, HandlerMode.ITEM)
    ```

!!! warning "Handler ID"

    The handler ID is automatically generated from the class name in snake_case:

    ```python
    class IsValidCouponCode  # -> id: 'is_valid_coupon_code'
    class ProductSKU         # -> id: 'product_sku'
    ```

!!! note "Error Templates"

    Provide clear, user-friendly error messages:

    ```python
    ERROR_TEMPLATES = {
        HandlerMode.ROOT: lambda self: f"Clear message with {self.value} and {self.argument}"
    }
    ```

---

## Registering Custom Handlers

After creating your custom handler, register it with `Pipe`:

```python
# For conditions
Pipe.Condition.MyCustomCondition = MyCustomCondition

# For matches
Pipe.Match.Format.MyCustomMatch = MyCustomMatch
# or
Pipe.Match.Text.MyCustomMatch = MyCustomMatch

# For transforms
Pipe.Transform.MyCustomTransform = MyCustomTransform
```

Then use it like any built-in handler:

```python
result = Pipe(
    value="test",
    type=str,
    conditions={Pipe.Condition.MyCustomCondition: argument},
    matches={Pipe.Match.Format.MyCustomMatch: argument},
    transform={Pipe.Transform.MyCustomTransform: argument}
).run()
```

---

## Next Steps

-   Learn about [Error Customization](customization.md) to customize error messages
-   Explore [Handler Modifiers](modifiers.md) to use `Item()` and `Context()` with your handlers
-   Check [Pipeline Hooks](hooks.md) for pre/post processing logic
