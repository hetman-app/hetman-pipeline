from pipeline.handlers.base_handler.resources.exceptions import \
    HandlerException


class ConditionException(HandlerException):
    pass


class ConditionMissingRootErrorMsg(ConditionException):
    def __init__(self) -> None:
        error: str = "Root error message is missing from the condition. It is required."

        super().__init__(error)
