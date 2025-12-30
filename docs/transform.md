# Transform Stage

The **Transform** stage is the final step in the `Pipe` lifecycle. It is reached **only if all Conditions and Matches have passed**.

It modifies the value into its final form before it is returned by the pipeline or passed to your function.

!!! tip "Data Integrity"

    Because Transformation happens last, you are guaranteed to be transforming data that has already been verified as valid, preventing errors like trying to `.strip()` an `Integer` or a `None` value.

---

## Setup vs Transform: When to Use Each

Both `setup` and `transform` use transform handlers, but they run at different stages of the Pipe lifecycle:

| Feature | Setup | Transform |
|---------|-------|-----------|
| **When it runs** | After type validation, **before** conditions/matches | After all validations pass (**final** stage) |
| **Purpose** | Data preparation and normalization | Data modification and formatting |
| **Validation** | Only type is validated | All conditions and matches have passed |
| **Use case** | Strip whitespace, normalize input | Format output, apply business logic |

### Example: Setup for Preparation

Use `setup` when you need to normalize data **before** validation:

```python
from pipeline.core.pipe.pipe import Pipe

# Setup strips whitespace BEFORE checking email format
result = Pipe(
    value="  user@example.com  ",
    type=str,
    setup={Pipe.Transform.Strip: None},  # Runs first
    matches={Pipe.Match.Format.Email: None},  # Validates cleaned value
).run()

print(result.value)  # "user@example.com" (no spaces)
```

### Example: Transform for Formatting

Use `transform` when you need to modify data **after** validation:

```python
from pipeline.core.pipe.pipe import Pipe

# Transform lowercases AFTER validation passes
result = Pipe(
    value="User@Example.COM",
    type=str,
    matches={Pipe.Match.Format.Email: None},  # Validates first
    transform={Pipe.Transform.Lowercase: None}  # Formats after validation
).run()

print(result.value)  # "user@example.com"
```

### Combining Setup and Transform

You can use both together for a complete data processing pipeline:

```python
from pipeline.core.pipe.pipe import Pipe

result = Pipe(
    value="  User@Example.COM  ",
    type=str,
    setup={Pipe.Transform.Strip: None},  # 1. Clean input
    conditions={Pipe.Condition.MaxLength: 50},  # 2. Validate structure
    matches={Pipe.Match.Format.Email: None},  # 3. Validate format
    transform={Pipe.Transform.Lowercase: None}  # 4. Format output
).run()

print(result.value)  # "user@example.com"
```

!!! tip "Setup vs Pre-Hook"
    While `pre_hook` can perform the same data preparation as `setup`, the `setup` argument is a **developer-friendly simplification**. **Important**: `setup` is **per-pipe** (field-specific), while `pre_hook` is **global** (applies to all fields in a Pipeline). Use `setup` for field-specific transformations and `pre_hook` for global logic or complex custom logic.

---

## Advanced: Custom Transformation Logic

While transformations are powerful, sometimes you need custom logic. Use hooks for this:

```python
from pipeline.core.pipeline.pipeline import Pipeline
from pipeline.core.pipe.pipe import Pipe

# Create pipeline
user_pipeline = Pipeline(
    name={"type": str},
    email={"type": str}
)

# Add custom transformation via pre_hook
def custom_transform(hook):
    current_value = hook.value.get
    if hook.field == "name":
        # Custom logic: Title case
        hook.value.set(current_value.title())
    elif hook.field == "email":
        # Custom logic: Lowercase and strip
        hook.value.set(current_value.lower().strip())

user_pipeline.pre_hook = custom_transform

result = user_pipeline.run(data={
    "name": "john doe",
    "email": "  User@Example.COM  "
})

print(result.processed_data)
# {
#     'name': 'John Doe',
#     'email': 'user@example.com'
# }
```

---

## Best Practices

!!! tip "Order Matters"

    Transformations are applied in the order they're defined:

    ```text
    transform={
        Pipe.Transform.Strip: None,      # 1. Remove whitespace
        Pipe.Transform.Lowercase: None,  # 2. Convert to lowercase
        Pipe.Transform.Capitalize: None  # 3. Capitalize
    }
    ```

!!! tip "Combine with Validation"

    Always validate before transforming:

    ```text
    email={
        "type": str,
        "conditions": {Pipe.Condition.MaxLength: 64},  # Validate
        "matches": {Pipe.Match.Format.Email: None},    # Validate
        "transform": {Pipe.Transform.Lowercase: None}  # Transform
    }
    ```

!!! warning "Type Safety"

    Transformations only run if validation passes, ensuring type safety:

    ```text
    # If value is not a string, Lowercase won't run
    Pipe(
        value=123,  # Wrong type
        type=str,
        transform={Pipe.Transform.Lowercase: None}
    )
    ```

---

## Technical Reference

The following section is automatically generated from the source code, detailing transformation handlers like string manipulation, math operations, and unique filtering.

::: pipeline.handlers.transform_handler.transform
