from functools import wraps
from typing import Any, ClassVar

from pipeline.core.pipe.resources.types import PipeContext
from pipeline.core.pipeline.resources.constants import (
    PipelineHook, PipelineResult
)
from pipeline.core.pipeline.resources.exceptions import PipelineException
from pipeline.core.pipeline.resources.types import (
    PipelineHandleErrorsFunc, PipelineHookFunc, PipelinePipeConfig
)
from pipeline.handlers.condition_handler.resources.types import ConditionErrors


class Pipeline:
    """
    The Pipeline class orchestrates the execution of multiple pipes on a data dictionary.

    It allows defining a sequence of processing steps (pipes) for specific fields in the input data.
    The pipeline iterates over the configuration, applies the corresponding pipe to each field,
    and aggregates any errors encountered.
    Hooks can be registered to execute before and after each pipe, allowing for side effects or
    custom logic. A custom error handler can also be provided to process aggregated errors.

    Attributes:
        global_pre_hook (ClassVar[PipelineHookFunc | None]): A function to be called before each pipe execution.
        global_post_hook (ClassVar[PipelineHookFunc | None]): A function to be called after each pipe execution.
        global_handle_errors (ClassVar[PipelineHandleErrorsFunc | None]): A function to handle
            errors collected during pipeline execution. This could be used to raise exceptions,
            log errors, or format them for a response.
    """
    global_pre_hook: ClassVar[PipelineHookFunc | None] = None
    """A function to be called before each pipe execution."""

    global_post_hook: ClassVar[PipelineHookFunc | None] = None
    """A function to be called after each pipe execution."""

    global_handle_errors: ClassVar[PipelineHandleErrorsFunc | None] = None
    """A function to handle errors collected during pipeline execution."""
    def __init__(
        self,
        pre_hook: PipelineHookFunc | None = None,
        post_hook: PipelineHookFunc | None = None,
        handle_errors: PipelineHandleErrorsFunc | None = None,
        **pipes_config: PipelinePipeConfig
    ) -> None:
        """
        Initializes the Pipeline with a configuration of pipes.

        The `pipes_config` defines the schema and validation rules for the data. Each key in
        `pipes_config` corresponds to a key in the input data dictionary. The value is a
        dictionary of arguments required to initialize a `Pipe` instance (e.g., `type`,
        `conditions`, `matches`).

        Args:
            pre_hook (PipelineHookFunc | None): A function to be called before each pipe execution.
                The global_pre_hook will not run if a local pre_hook is defined.
            post_hook (PipelineHookFunc | None): A function to be called after each pipe execution.
                The global_post_hook will not run if a local pre_hook is defined.
            handle_errors (PipelineHandleErrorsFunc | None): A function to handle
                errors collected during pipeline execution. This could be used to raise exceptions,
                log errors, or format them for a response. The global_handle_errors will not run
                if a local handle_errors is defined.
            **pipes_config (PipelinePipeConfig): Configuration for the pipes.
                Keys represent the fields in the data dictionary to be processed,
                and values are the configuration for the corresponding pipe.
        """
        self.pre_hook: PipelineHookFunc | None = pre_hook
        self.post_hook: PipelineHookFunc | None = post_hook

        self.handle_errors: PipelineHandleErrorsFunc | None = handle_errors

        self.pipes_config: dict[str, PipelinePipeConfig] = pipes_config

        self._errors: dict[str, ConditionErrors] = {}
        self._processed_data: dict = {}

    def run(self, data: dict) -> PipelineResult:
        """
        Runs the pipeline on the provided data.

        This method iterates through the `pipes_config`. For each field, it executes
        the internal `self._process_field_pipe` method.

        After processing all fields, if `handle_errors` is defined, it is called with the
        collected errors.

        Args:
            data (dict): The input data dictionary to process. The dictionary may be modified in-place
                with transformed values.

        Returns:
            PipelineResult: A namedtuple containing the fields errors and processed_data. The processed_data field contains the final, trustworthy data and will be `None` if there are errors.
        """
        context: PipeContext = data

        for field, pipe_config in self.pipes_config.items():
            self._process_field_pipe(
                data=data,
                context=context,
                field=field,
                pipe_config=pipe_config
            )

        if self._errors and self.handle_errors:
            self.handle_errors(self._errors)

        return PipelineResult(
            errors=self._errors or None,
            processed_data=None if self._errors else self._processed_data
        )

    def _process_field_pipe(
        self, data: dict, context: PipeContext, field: str,
        pipe_config: PipelinePipeConfig
    ) -> None:
        """
        Internal function that runs the pipe on a specific field and manages hooks.

        The execution flow is as follows:
        1. Value extraction: Retrieves the initial value from the input data.
        2. Hook preparation: Defines a closure-based Value class using nonlocal 
           to allow hooks to get or set the variable directly in the local scope.
        3. Pre-hook execution: Runs the local pre_hook if defined. Otherwise, 
           falls back to the Pipeline.global_pre_hook.
        4. Context Management: If the current value is a dictionary, it overrides 
           the context for the downstream pipe execution.
        5. Pipe execution: Initializes and runs a Pipe instance to handle 
           validation, matching, and transformation.
        6. Error handling: Checks for condition_errors or match_errors. If found, 
           the field is marked invalid and errors are stored in self._errors.
        7. Post-Hook Execution: Updates the hook's is_valid state and executes 
           the local or global post-hook.
        8. Data Persistence: Saves the final value to self._processed_data.

        Args:
            data: The source dictionary containing the field value.
            context: The shared context for the pipeline execution.
            field: The name of the field being processed.
            pipe_config: Configuration parameters for the specific pipe.
        """
        from pipeline.core.pipe.pipe import Pipe

        value: Any = data.get(field, None)

        class Value:
            @property
            def get(self) -> Any:
                nonlocal value

                return value

            def set(self, new_value: Any) -> Any:
                nonlocal value

                value = new_value

                return self.get

        hook = PipelineHook(
            field=field, value=Value(), is_valid=None, pipe_config=pipe_config
        )

        if self.pre_hook:
            self.pre_hook(hook)
        elif Pipeline.global_pre_hook:
            Pipeline.global_pre_hook(hook)

        if isinstance(value, dict):
            context = value

        pipe: Pipe = Pipe(value=value, **pipe_config, context=context)

        value, condition_errors, match_errors = pipe.run()

        is_valid: bool = not bool(condition_errors or match_errors)

        if not is_valid:
            self._errors[field] = [*condition_errors, *match_errors]

        hook.is_valid = is_valid

        if self.post_hook:
            self.post_hook(hook)
        elif Pipeline.global_post_hook:
            Pipeline.global_post_hook(hook)

        self._processed_data[field] = value

    def __call__(self, func: Any) -> Any:
        """
        Decorator to run the pipeline before a function execution.

        When the decorated function is called, the pipeline is run using the function's
        keyword arguments (`kwargs`) as the input data. If validation fails, and no
        `handle_errors` is provided, a `PipelineException` is raised.

        Args:
            func (Any): The function to be decorated. The pipeline will run on the
                keyword arguments passed to this function.

        Returns:
            Any: The wrapped function.

        Raises:
            PipelineException: If the pipeline encounters errors and no error handler is defined.
        """
        @wraps(func)
        def wrapper(*args, **kwargs):
            result: PipelineResult = self.run(data=kwargs)

            if result.errors and not self.handle_errors or result.processed_data is None:
                raise PipelineException(result.errors)

            kwargs = {**kwargs, **result.processed_data}

            return func(*args, **kwargs)

        return wrapper
