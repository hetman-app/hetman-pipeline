from pipeline.handlers.base_handler.base_handler import Flag


class ConditionFlag(Flag):
    RETURN_ONLY_ERROR_MSG = "RETURN_ONLY_ERROR_MSG"
    BREAK_PIPE_LOOP_ON_ERROR = "BREAK_PIPE_LOOP_ON_ERROR"
