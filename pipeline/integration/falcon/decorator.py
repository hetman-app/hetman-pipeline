import inspect
import json
from functools import wraps
from typing import Callable, cast

from pipeline.core.pipeline.resources.constants import PipelineResult

try:
    from falcon import Request as RequestSync
    from falcon import Response as ResponseSync
    from falcon.asgi import Request as RequestAsync
    from falcon.asgi import Response as ResponseAsync
except ImportError:
    raise ImportError(
        "Falcon package is required. Install it using:"
        "pip install hetman-pipeline[falcon]"
    )

from pipeline.core.pipeline.pipeline import Pipeline
from pipeline.core.pipeline.resources.types import (
    PipelineHandleErrorsFunc, PipelineHookFunc, PipelinePipeConfig
)


class PipelineFalcon(Pipeline):
    pass


def process_request(
    pre_hook: PipelineHookFunc | None = None,
    post_hook: PipelineHookFunc | None = None,
    handle_errors: PipelineHandleErrorsFunc | None = None,
    **pipes_config: PipelinePipeConfig
):
    """
    A decorator factory that validates Falcon request (WSGI and ASGI) data
    using a defined pipeline.

    This decorator extracts data from a Falcon `Request` object (either from 
    query parameters for GET requests or the media body for other methods), 
    runs it through a `PipelineFalcon` instance, and injects the validated 
    data into the decorated responder method.

    If validation fails, it automatically sets the response body to the 
    validation errors and returns a 400 Bad Request status, preventing 
    the responder from executing. You can use your own error handler via
    `PipelineFalcon.handle_errors`, but it must end the request.

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

    Returns:
        Callable: A decorator that wraps a Falcon responder method.

    Example:
        @request_validator(
            email={
                "type": str,
                "conditions": {
                    Pipe.Condition.MaxLength: 64
                },
                "matches": {
                    Pipe.Match.Format.Email: None
                }
            }
        )
        def on_post(self, req, resp, email):
            pass
    """
    def decorator(responder: Callable):
        is_async: bool = inspect.iscoroutinefunction(responder)

        def get_params(req: RequestSync | RequestAsync) -> dict:
            data: dict = cast(dict, req.params)

            for field, value in data.items():
                try:
                    data[field] = json.loads(value)
                except (json.JSONDecodeError, TypeError):
                    pass

            return data

        def run_pipeline(data: dict) -> PipelineResult:
            return PipelineFalcon(
                pre_hook=pre_hook,
                post_hook=post_hook,
                handle_errors=handle_errors,
                **pipes_config
            ).run(data=data)

        def handle_result(
            resp: ResponseSync | ResponseAsync, result: PipelineResult
        ) -> bool:
            if result.errors:
                resp.media = result.errors
                resp.status = 400

                return True

            return False

        if is_async:

            @wraps(responder)
            async def async_wrapper(
                resource: object, req: RequestAsync, resp: ResponseAsync, *args,
                **kwargs
            ):
                data: dict

                if req.method.upper() == "GET":
                    data = get_params(req=req)
                else:
                    data = await req.get_media({})

                result: PipelineResult = run_pipeline(data)

                if handle_result(
                    resp=resp, result=result
                ) or result.processed_data is None:
                    return

                return await responder(
                    resource, req, resp, *args, **kwargs,
                    **result.processed_data
                )

            return async_wrapper
        else:

            @wraps(responder)
            def sync_wrapper(
                resource: object, req: RequestSync, resp: ResponseAsync, *args,
                **kwargs
            ):
                data: dict

                if req.method.upper() == "GET":
                    data = get_params(req=req)
                else:
                    data = req.get_media({})

                result: PipelineResult = run_pipeline(data)

                if handle_result(
                    resp=resp, result=result
                ) or result.processed_data is None:
                    return

                return responder(
                    resource, req, resp, *args, **kwargs,
                    **result.processed_data
                )

            return sync_wrapper

    return decorator
