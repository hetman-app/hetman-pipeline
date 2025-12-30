# Transform Stage

The **Transform** stage is the final step in the `Pipe` lifecycle. It is reached **only if all Conditions and Matches have passed**.

It modifies the value into its final form before it is returned by the pipeline or passed to your function.

!!! tip "Data Integrity"

    Because Transformation happens last, you are guaranteed to be transforming data that has already been verified as valid, preventing errors like trying to `.strip()` an `Integer` or a `None` value.

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
