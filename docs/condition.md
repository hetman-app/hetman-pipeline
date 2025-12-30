# Condition Stage

The **Condition** stage is the first step in the `Pipe` lifecycle. It is responsible for validating the fundamental integrity of the data, such as its type, presence, size, and basic constraints.

!!! info "Execution Rule"

    If a condition fails, the pipe execution will **not stop immediately**. It will evaluate every condition to gather all errors. However, certain conditions have a special flag `ConditionFlag.BREAK_PIPE_LOOP_ON_ERROR` (such as `Condition.ValueType`) that breaks the loop upon an error.

---

## Technical Reference

The following section is automatically generated from the source code, detailing the available condition handlers and their configurations.

::: pipeline.handlers.condition_handler.condition
