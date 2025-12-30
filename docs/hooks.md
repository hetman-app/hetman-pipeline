# Pipeline Hooks

Hooks are powerful mechanisms that allow you to inject custom logic before and after each pipe execution in a pipeline. They enable side effects like logging, data sanitization, redaction, and more.

---

## Hook Types

### `pre_hook`

Executed **before** each pipe runs. Perfect for:

-   Global data sanitization (e.g., stripping whitespace)
-   Preprocessing values
-   Logging incoming data
-   Modifying values before validation

### `post_hook`

Executed **after** each pipe runs. Perfect for:

-   Logging validation results
-   Redacting sensitive data
-   Side effects based on validation status
-   Collecting metrics

---

## The PipelineHook Object

Both hooks receive a `PipelineHook` object with the following properties:

| Property      | Type           | Description                                                 |
| ------------- | -------------- | ----------------------------------------------------------- |
| `field`       | `str`          | The name of the field being processed                       |
| `value`       | `Value`        | Value object with `.get` property and `.set()` method       |
| `is_valid`    | `bool or None` | Validation status (`None` in pre_hook, `bool` in post_hook) |
| `pipe_config` | `dict`         | The pipe configuration including metadata                   |

### Accessing and Modifying Values

The `hook.value` object uses a closure-based mechanism to allow direct manipulation of values during pipe execution.

!!! note "Value Class Mechanism"

    - `hook.value.get` is a **property** (not a method) - access it without parentheses
    - `hook.value.set(new_value)` is a **method** - call it with parentheses
    - The Value class uses Python's `nonlocal` to modify the actual value in the pipeline's scope

```python
def my_hook(hook):
    # Get the current value (property access)
    current_value = hook.value.get

    # Set a new value (method call)
    hook.value.set("new value")

    # Common pattern: conditional modification
    if isinstance(current_value, str):
        hook.value.set(current_value.strip())
```

---

## Three Levels of Customization

Hetman Pipeline offers **three flexible ways** to customize hooks, from global to specific:

### 1. Global Class-Level Hooks

Set hooks globally for **all instances** of the `Pipeline` class:

```python
from pipeline.core.pipeline.pipeline import Pipeline
from pipeline.core.pipe.pipe import Pipe

# Define global hooks
def global_pre_hook(hook):
    """Strip all string values globally"""
    current_value = hook.value.get

    if isinstance(current_value, str):
        hook.value.set(current_value.strip())

def global_post_hook(hook):
    """Log all validation failures globally"""
    if not hook.is_valid:
        print(f"[X] Field '{hook.field}' failed validation")

# Set globally for ALL Pipeline instances
Pipeline.global_pre_hook = global_pre_hook
Pipeline.global_post_hook = global_post_hook

# Now ALL pipelines will use these hooks
pipeline1 = Pipeline(
    name={"type": str, "conditions": {Pipe.Condition.MaxLength: 10}}
)

pipeline2 = Pipeline(
    email={"type": str, "matches": {Pipe.Match.Format.Email: None}}
)

# Both pipelines will strip strings and log failures
pipeline1.run(data={"name": "  John  "})  # Strips whitespace
pipeline2.run(data={"email": "invalid"})  # Logs failure
```

---

### 2. Instance-Level Hooks

Set hooks for a **specific pipeline instance**:

```python
from pipeline.core.pipeline.pipeline import Pipeline
from pipeline.core.pipe.pipe import Pipe

# Create a pipeline
user_pipeline = Pipeline(
    username={
        "type": str,
        "conditions": {Pipe.Condition.MaxLength: 20}
    },
    password={
        "type": str,
        "matches": {
            Pipe.Match.Format.Password: Pipe.Match.Format.Password.STRICT
        },
        "metadata": {
            "sensitive": True
        }
    },
    email={
        "type": str,
        "matches": {
            Pipe.Match.Format.Email: None
        }
    }
)

# Set instance-specific hooks
def sanitize_input(hook):
    """Sanitize input for this specific pipeline"""
    if isinstance(hook.value.get, str):
        # Remove leading/trailing whitespace
        hook.value.set(hook.value.get.strip())

def redact_sensitive_data(hook):
    """Redact sensitive fields in logs"""
    status = "OK" if hook.is_valid else "X"

    metadata = hook.pipe_config.get('metadata', {})

    if metadata.get('sensitive'):
        print(f"[{status}] Field '{hook.field}': [REDACTED]")
    else:
        print(f"[{status}] Field '{hook.field}': {hook.value.get}")

# Attach to this instance only
user_pipeline.pre_hook = sanitize_input
user_pipeline.post_hook = redact_sensitive_data

# Run the pipeline
result = user_pipeline.run(data={
    "username": "  john_doe  ",
    "password": "SecurePass123!",
    "email": "john@example.com"
})

# Output:
# [OK] Field 'username': john_doe
# [OK] Field 'password': [REDACTED]
# [OK] Field 'email': john@example.com
```

---

### 3. Inheritance-Based Customization

Create a **custom Pipeline subclass** with built-in hook logic:

```python
from pipeline.core.pipeline.pipeline import Pipeline
from pipeline.core.pipe.pipe import Pipe
import logging

class LoggingPipeline(Pipeline):
    """Custom Pipeline with built-in logging and sanitization"""

    def __init__(self, **pipes_config):
        super().__init__(
            pre_hook=self._sanitize_and_log_input,
            post_hook=self._log_validation_result,
            **pipes_config
        )

        # Set up logger
        self.logger = logging.getLogger(self.__class__.__name__)

    def _sanitize_and_log_input(self, hook):
        """Sanitize and log incoming data"""
        self.logger.info(f"Processing field: {hook.field}")

        original_value = hook.value.get

        # Auto-strip strings
        if isinstance(original_value, str):
            sanitized = original_value.strip()

            if original_value != sanitized:
                self.logger.debug(f"Sanitized '{hook.field}': '{original_value}' -> '{sanitized}'")

            hook.value.set(sanitized)

    def _log_validation_result(self, hook):
        """Log validation results with metadata awareness"""
        metadata = hook.pipe_config.get('metadata', {})

        # Check if field should be redacted
        if metadata.get('redact_in_logs'):
            display_value = "[REDACTED]"
        else:
            display_value = hook.value.get

        if not hook.is_valid:
            self.logger.error(f"[X] Validation failed for '{hook.field}'")
        else:
            self.logger.info(f"[OK] '{hook.field}': {display_value}")


# Usage
logging.basicConfig(level=logging.DEBUG)

api_pipeline = LoggingPipeline(
    api_key={
        "type": str,
        "conditions": {Pipe.Condition.MinLength: 32},
        "metadata": {"redact_in_logs": True}
    },
    username={
        "type": str,
        "conditions": {Pipe.Condition.MaxLength: 20}
    }
)

result = api_pipeline.run(data={
    "api_key": "super_secret_key_12345678901234567890",
    "username": "  admin  "
})

# Logs:
# INFO:LoggingPipeline:Processing field: api_key
# INFO:LoggingPipeline:[OK] 'api_key': [REDACTED]
# INFO:LoggingPipeline:Processing field: username
# DEBUG:LoggingPipeline:Sanitized 'username': '  admin  ' -> 'admin'
# INFO:LoggingPipeline:[OK] 'username': admin
```

---

## Advanced Example: Multi-Tenant Pipeline

Combine inheritance with instance customization for maximum flexibility:

```python
from pipeline.core.pipeline.pipeline import Pipeline
from pipeline.core.pipe.pipe import Pipe
from datetime import datetime

class AuditPipeline(Pipeline):
    """Pipeline with built-in audit trail"""

    def __init__(self, tenant_id: str, **pipes_config):
        super().__init__(
            pre_hook=self._audit_pre,
            post_hook=self._audit_post,
            **pipes_config
         )

        self.tenant_id = tenant_id
        self.audit_log = []

    def _audit_pre(self, hook):
        """Record incoming data"""
        self.audit_log.append({
            "timestamp": datetime.now().isoformat(),
            "tenant": self.tenant_id,
            "field": hook.field,
            "action": "input",
            "value": hook.value.get
        })

    def _audit_post(self, hook):
        """Record validation results"""
        self.audit_log.append({
            "timestamp": datetime.now().isoformat(),
            "tenant": self.tenant_id,
            "field": hook.field,
            "action": "validated",
            "is_valid": hook.is_valid,
            "final_value": hook.value.get
        })

    def get_audit_trail(self):
        """Retrieve audit trail"""
        return self.audit_log


# Create tenant-specific pipelines
tenant_a_pipeline = AuditPipeline(
    tenant_id="tenant_a",
    email={"type": str, "matches": {Pipe.Match.Format.Email: None}}
)

tenant_b_pipeline = AuditPipeline(
    tenant_id="tenant_b",
    email={"type": str, "matches": {Pipe.Match.Format.Email: None}}
)

# Process data
tenant_a_pipeline.run(data={"email": "user@tenant-a.com"})
tenant_b_pipeline.run(data={"email": "invalid-email"})

# View audit trails
print("Tenant A Audit:", tenant_a_pipeline.get_audit_trail())
print("Tenant B Audit:", tenant_b_pipeline.get_audit_trail())
```

---

## Best Practices

!!! tip "When to Use Each Approach"

    - **Global hooks**: Use for application-wide behavior (e.g., security sanitization)
    - **Instance hooks**: Use for specific pipeline behavior (e.g., API endpoint validation)
    - **Inheritance**: Use when you need reusable pipeline variants with custom logic

!!! warning "Hook Execution Order"

    **Execution Flow:**

    1. `pre_hook` is called **before** pipe validation
    2. Pipe runs (condition -> match -> transform)
    3. `post_hook` is called **after** pipe completes (even if pipe is invalid)

    **Priority (which hook runs):**

    - If instance-level hook is defined (`pipeline.pre_hook` or `pipeline.post_hook`), it runs
    - Otherwise, global class-level hook runs (`Pipeline.global_pre_hook` or `Pipeline.global_post_hook`)
    - Instance hooks **override** global hooks (they don't run together)

!!! note "Modifying Values"

    Always use `hook.value.set()` to modify values in hooks. Use `hook.value.get` to read:

    ```text
    # [X] Wrong
    def bad_hook(hook):
        hook.value = hook.value.strip()

    # [OK] Correct
    def good_hook(hook):
        current = hook.value.get
        if isinstance(current, str):
            hook.value.set(current.strip())
    ```

---

## Next Steps

-   Learn about [Handler Modifiers](modifiers.md) for advanced value processing
-   Explore [Error Customization](customization.md) for custom error messages
-   Check [Framework Integrations](integrations.md) for Falcon and other frameworks
