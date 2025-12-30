# Match Stage

The **Match** stage is the second step in the `Pipe` lifecycle. It is executed **only if all previous Conditions have passed**.

While Conditions check for structural integrity (type and size), the Match stage focuses on **semantic validation** - ensuring the content of the data follows a specific pattern or format.

!!! info "Execution Rule"

    The Match stage is the bridge between "is this data the right shape?" and "is this data the right content?". It is primarily powered by Regular Expressions (Regex) and format-specific validators.

---

## Best Practices

!!! tip "Combine with Conditions"

    Use conditions for structural validation, then match for content:

    ```python
    email={
        "type": str,
        "conditions": {Pipe.Condition.MaxLength: 64},  # Structure
        "matches": {Pipe.Match.Format.Email: None}      # Content
    }
    ```

!!! tip "Use Appropriate Validators"

    Choose the right validator for your use case:

    - **Email**: Use `Match.Format.Email`
    - **URL**: Use `Match.Web.URL`
    - **Phone**: Use `Match.Format.E164Phone`
    - **Custom patterns**: Use `Match.Regex.FullMatch` or `Match.Regex.Search`

!!! warning "Regex Performance"

    Complex regex patterns can be slow. Test performance with realistic data:

    ```python
    # Simple and fast
    r"^\d{5}$"

    # Complex and potentially slow
    r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$"
    ```

    Run conditions before match to increase performance:

    ```python
    email={
        "type": str,
        "conditions": {Pipe.Condition.MaxLength: 64},  # Structure
        "matches": {Pipe.Match.Format.Email: None}      # Content
    }
    ```

!!! warning "Case Sensitivity"

    Most match handlers are case-sensitive.

---

## Technical Reference

The following section is automatically generated from the source code, detailing the available condition handlers and their configurations.

::: pipeline.handlers.match_handler.match

::: pipeline.handlers.match_handler.units.match_encoding
::: pipeline.handlers.match_handler.units.match_format
::: pipeline.handlers.match_handler.units.match_localization
::: pipeline.handlers.match_handler.units.match_network
::: pipeline.handlers.match_handler.units.match_regex
::: pipeline.handlers.match_handler.units.match_text
::: pipeline.handlers.match_handler.units.match_time
::: pipeline.handlers.match_handler.units.match_web
