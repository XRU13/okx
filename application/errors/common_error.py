class AppError(Exception):
    """
    Base class for application logic errors.
    """
    msg_template: str = None

    def __init__(self, **kwargs):
        self.context = kwargs.pop('context', {})

        if 'message' in kwargs:
            self.message = kwargs['message']
        elif self.msg_template:
            self.message = self.msg_template.format(**kwargs)
        else:
            self.message = None

    def __str__(self):
        return self.message


class GetCurseError(AppError):
    msg_template = 'Get course error for pair: "{pair}"'


class GerMethodError(AppError):
    msg_template = 'Get method error for method name: "{method}"'


class GerPlatformError(AppError):
    msg_template = 'Get platform error for platform name: "{platform}"'


class GetLoopError(AppError):
    msg_template = 'Get loop error for loop_id: "{loop_id}"'
