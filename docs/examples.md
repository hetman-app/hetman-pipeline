# Usage & Examples

Hetman Pipeline is designed to be flexible, allowing you to use it as a standalone validator for single values, a schema-based orchestrator for dictionaries, or a decorator for type-safe functions.

---

## 1. Single Pipe Validation

A `Pipe` is the smallest unit of logic. It allows you to validate a single value against specific conditions, matches, and transformations.

```python
from pipeline.core.pipe.pipe import Pipe

pipe = Pipe(
    value="john.SMITH@example.com",
    type=str,
    conditions={Pipe.Condition.MaxLength: 64},
    matches={Pipe.Match.Format.Email: None},
    transform={Pipe.Transform.Lowercase: None}
)

result = pipe.run()
print(result.value)  # john.smith@example.com
print(result.condition_errors)  # []
print(result.match_errors)  # []
```

---

## 2. Schema-based Pipeline

The `Pipeline` class allows you to define complex schemas for dictionaries. It supports nested pipelines, metadata handling, and custom hooks.

```python
from pipeline.core.pipeline.pipeline import Pipeline
from pipeline.core.pipe.pipe import Pipe

# Define a pipeline for a 'Person' object
person_pipeline = Pipeline(
    name={
        "type": str,
        "conditions": {Pipe.Condition.MaxLength: 50},
        "matches": {Pipe.Match.Text.Letters: None},
        "transform": {Pipe.Transform.Capitalize: None}
    },
    age={
        "type": int,
        "conditions": {
            Pipe.Condition.MinNumber: 0,
            Pipe.Condition.MaxNumber: 120
        }
    },
    email={
        "type": str,
        "conditions": {Pipe.Condition.MaxLength: 64},
        "matches": {Pipe.Match.Format.Email: None},
        "transform": {Pipe.Transform.Lowercase: None}
    },
    bio={
        "type": str,
        "conditions": {Pipe.Condition.MaxLength: 500},
        "matches": {Pipe.Match.Text.Printable: None},
        "optional": True
    }
)

# Validate data
result = person_pipeline.run(data={
    "name": "john",
    "age": 30,
    "email": "John@Example.com"
})

print(result.processed_data, result.errors)
# {
#     'name': 'John',  # Capitalized
#     'age': 30,
#     'email': 'john@example.com',  # Lowercased
#     'bio': None
# }
```

---

## 3. Using Handler Modifiers

### Item() - Validate Collection Items

Apply validation to each item in a list or dictionary:

```python
from pipeline.core.pipe.pipe import Pipe
from pipeline.handlers.base_handler.handler_modifiers import Item

# Validate a list of email addresses
result = Pipe(
    value=["aDMIN@company.com", "user@comPANy.com", "support@COmpany.com"],
    type=list,
    matches={
        Item(Pipe.Match.Format.Email): None
    },
    transform={
        Item(Pipe.Transform.Lowercase): None
    }
).run()

print(result.value)
# ['admin@company.com', 'user@company.com', 'support@company.com']
```

### Context() - Use Values from Pipeline Context

Validate fields based on other field values:

```python
from pipeline.core.pipeline.pipeline import Pipeline
from pipeline.core.pipe.pipe import Pipe
from pipeline.handlers.base_handler.handler_modifiers import Context

# Password confirmation example
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
            Context(Pipe.Condition.MatchesField): "password"
        }
    }
)

result = registration_pipeline.run(data={
    "password": "SecurePass123!",
    "password_confirm": "Secure"
})

print(result.errors)
# {'password_confirm': [{'id': 'matches_field', 'msg': 'This must match the password field.', 'value': 'Secure'}]}
```

---

## 4. Pipeline Hooks

Hooks allow you to inject custom logic before and after each pipe execution.

### Pre-Hook: Global Sanitization

```python
from pipeline.core.pipeline.pipeline import Pipeline
from pipeline.core.pipe.pipe import Pipe

# Define a pipeline
user_pipeline = Pipeline(
    username={
        "type": str,
        "conditions": {Pipe.Condition.MaxLength: 20}
    },
    email={
        "type": str,
        "matches": {Pipe.Match.Format.Email: None}
    }
)

# Attach a pre-hook to strip whitespace from all strings
def sanitize_strings(hook):
    current_value = hook.value.get

    if isinstance(current_value, str):
        hook.value.set(current_value.strip())

user_pipeline.pre_hook = sanitize_strings

# Now all string values will be stripped before validation
result = user_pipeline.run(data={
    "username": "  john_doe  ",
    "email": "  john@example.com  "
})

print(result.processed_data)
# {'username': 'john_doe', 'email': 'john@example.com'}
```

### Post-Hook: Logging and Redaction

```python
from pipeline.core.pipeline.pipeline import Pipeline
from pipeline.core.pipe.pipe import Pipe

# Pipeline with sensitive data
auth_pipeline = Pipeline(
    username={"type": str},
    password={
        "type": str,
        "matches": {Pipe.Match.Format.Password: Pipe.Match.Format.Password.STRICT},
        "metadata": {"sensitive": True}
    },
    api_key={
        "type": str,
        "conditions": {Pipe.Condition.MinLength: 32},
        "metadata": {"sensitive": True}
    }
)

# Post-hook to redact sensitive fields in logs
def log_with_redaction(hook):
    status = "OK" if hook.is_valid else "X"

    metadata = hook.pipe_config.get('metadata', {})

    if metadata.get('sensitive'):
        print(f"[{status}] Field '{hook.field}': [REDACTED]")
    else:
        current_value = hook.value.get
        print(f"[{status}] Field '{hook.field}': {current_value}")

auth_pipeline.post_hook = log_with_redaction

result = auth_pipeline.run(data={
    "username": "admin",
    "password": "SecurePass123!",
    "api_key": "super_secret_key_12345678901234567890"
})

# Output:
# [OK] Field 'username': admin
# [OK] Field 'password': [REDACTED]
# [OK] Field 'api_key': [REDACTED]
```

---

## 5. Custom Pipeline Classes

Create reusable pipeline classes with built-in behavior:

```python
from pipeline.core.pipeline.pipeline import Pipeline
from pipeline.core.pipe.pipe import Pipe
import logging

class LoggingPipeline(Pipeline):
    """Pipeline with automatic logging"""

    def __init__(self, **pipes_config):
        super().__init__(
            pre_hook=self._log_input,
            post_hook=self._log_result,
            **pipes_config
        )

        self.logger = logging.getLogger(self.__class__.__name__)

    def _log_input(self, hook):
        self.logger.info(f"Validating field: {hook.field}")

    def _log_result(self, hook):
        if not hook.is_valid:
            self.logger.error(f"[X] Validation failed for '{hook.field}'")
        else:
            self.logger.info(f"[OK] '{hook.field}' validated successfully")

# Usage
logging.basicConfig(level=logging.INFO)

api_pipeline = LoggingPipeline(
    email={
        "type": str,
        "matches": {Pipe.Match.Format.Email: None}
    },
    age={
        "type": int,
        "conditions": {Pipe.Condition.MinNumber: 18}
    }
)

result = api_pipeline.run(data={
    "email": "user@example.com",
    "age": 25
})

# Logs:
# INFO:LoggingPipeline:Validating field: email
# INFO:LoggingPipeline:[OK] 'email' validated successfully
# INFO:LoggingPipeline:Validating field: age
# INFO:LoggingPipeline:[OK] 'age' validated successfully
```

---

## 6. Error Message Customization

Customize error messages for better user experience:

```python
from pipeline.handlers.condition_handler.resources.constants import ConditionFlag
from pipeline.handlers.condition_handler.condition_handler import ConditionHandler
from pipeline.core.pipe.pipe import Pipe
from pipeline.handlers.base_handler.resources.constants import HandlerMode

# Customize error messages
Pipe.Match.Format.Email.ERROR_TEMPLATES[HandlerMode.ROOT] = lambda _: (
    "Please provide a valid email address."
)

Pipe.Condition.MinLength.ERROR_TEMPLATES[HandlerMode.ROOT] = lambda self: (
    f"Must be at least {self.argument} characters long."
)

def my_error_builder(self: "ConditionHandler"):
    if ConditionFlag.RETURN_ONLY_ERROR_MSG in self.FLAGS:
        return self.error_msg

    return {'id': self.id, 'msg': self.error_msg, 'value': self.value, 'hello': 'world'}

# Also, you can define ERROR_BUILDER for a specific condition.
# It does not have to be global.
ConditionHandler.ERROR_BUILDER = my_error_builder

Pipe.Match.Format.Password.ERROR_MESSAGE[Pipe.Match.Format.Password.STRICT] = "I'm very strict."

Pipe.Match.Format.Password.ERROR_TEMPLATES[HandlerMode.ROOT] = lambda self: (
    f"Password requirements: {self.ERROR_MESSAGE[self.argument]}"
)

# Now errors will use custom messages
result = Pipe(
    value="ab",
    type=str,
    conditions={Pipe.Condition.MinLength: 8}
).run()

print(result.condition_errors)
# [{'id': 'min_length', 'msg': 'Must be at least 8 characters long.', 'value': 'ab', 'hello': 'world'}]
```

---

## 7. Function Decorators

Wrap functions to ensure arguments are validated before execution:

```python
from pipeline.core.pipeline.resources.exceptions import PipelineException
from pipeline.core.pipeline.pipeline import Pipeline
from pipeline.core.pipe.pipe import Pipe

@Pipeline(
    amount={
        'type': int,
        'conditions': {Pipe.Condition.MinNumber: 1},
        'transform': {Pipe.Transform.Multiply: 100}  # Convert to cents
    },
    currency={
        'type': str,
        'matches': {Pipe.Match.Localization.Currency: None},
        'transform': {Pipe.Transform.Reverse: None}
    }
)
def process_payment(amount, currency):
    # amount is already validated and converted to cents
    # currency is validated and reversed
    return f"Processing {amount} cents in {currency}"

# Valid call
result = process_payment(amount=50, currency="USD")
print(result)  # "Processing 5000 cents in DSU"

# Invalid call will raise PipelineException
try:
    process_payment(amount=-10, currency="USD")
except PipelineException as e:
    print(f"Error: {e}")
```

---

## 8. Nested Pipelines

Validate nested data structures:

```python
from pipeline.core.pipeline.pipeline import Pipeline
from pipeline.core.pipe.pipe import Pipe

# Define nested pipeline for address
address_pipeline = Pipeline(
    street={"type": str, "conditions": {Pipe.Condition.MaxLength: 100}},
    city={"type": str, "conditions": {Pipe.Condition.MaxLength: 50}},
    zip_code={
        "type": str,
        "matches": {Pipe.Match.Regex.FullMatch: r"^\d{5}$"}
    }
)

# Main pipeline with nested address
user_pipeline = Pipeline(
    name={"type": str, "conditions": {Pipe.Condition.MaxLength: 50}},
    email={
        "type": str,
        "matches": {Pipe.Match.Format.Email: None}
    },
    address={
        "type": dict,
        "conditions": {Pipe.Condition.Pipeline: address_pipeline}
    }
)

result = user_pipeline.run(data={
    "name": "John Doe",
    "email": "john@example.com",
    "address": {
        "street": "123 Main St",
        "city": "New York",
        "zip_code": "10001"
    }
})

print(result.processed_data)
```

---

## 9. Advanced: Multi-Level Validation

Combine multiple features for complex validation:

```python
from pipeline.core.pipeline.pipeline import Pipeline
from pipeline.core.pipe.pipe import Pipe
from pipeline.handlers.base_handler.handler_modifiers import Item

# E-commerce order validation
order_pipeline = Pipeline(
    customer_email={
        "type": str,
        "conditions": {Pipe.Condition.MaxLength: 64},
        "matches": {Pipe.Match.Format.Email: None},
        "transform": {Pipe.Transform.Lowercase: None}
    },
    items={
        "type": list,
        "conditions": {
            Pipe.Condition.MinLength: 1,
            Pipe.Condition.MaxLength: 50,
            Item(Pipe.Condition.IncludedIn): [
                "water",
                "sushi",
                "pizza"
            ]
        }
    },
    total_amount={
        "type": float,
        "conditions": {
            Pipe.Condition.MinNumber: 0.01,
            Pipe.Condition.MaxNumber: 10000.00
        }
    },
    discount_code={
        "type": str,
        "conditions": {Pipe.Condition.MaxLength: 20},
        "matches": {Pipe.Match.Text.Alphanumeric: None},
        "transform": {Pipe.Transform.Uppercase: None},
        "optional": True
    }
)

# Add hooks for business logic
def validate_total(hook):
    """Ensure total amount is reasonable"""
    current_value = hook.value.get

    if hook.field == "total_amount" and current_value > 5000:
        print(f"[!] Large order detected: ${current_value}")

# You can also pass a post_hook in __init__
order_pipeline.post_hook = validate_total

result = order_pipeline.run(data={
    "customer_email": "Customer@Example.com",
    "items": ["sushi", "pizza"],
    "total_amount": 299.99,
    "discount_code": "save*20"
})

print(result.processed_data)
# {
#     "customer_email": "customer@example.com",
#     "items": ["sushi", "pizza"],
#     "total_amount": 299.99,
#     "discount_code": "SAVE20",
# }
```

---

## Next Steps

-   **[Pipeline Hooks](hooks.md)** - Learn about pre_hook and post_hook in detail
-   **[Handler Modifiers](modifiers.md)** - Master Item() and Context() modifiers
-   **[Error Customization](customization.md)** - Customize error messages and templates
-   **[Framework Integrations](integrations.md)** - Integrate with Falcon and other frameworks
-   **[Lifecycle: Condition](condition.md)** - Explore condition handlers
-   **[Lifecycle: Match](match.md)** - Explore match handlers
-   **[Lifecycle: Transform](transform.md)** - Explore transformation handlers
