class WizError(Exception):

    def __init__(self, message, line=None, column=None):
        self.message = message
        self.line = line
        self.column = column

    def __str__(self):

        banner = (
            "\n"
            "╔══════════════════════════════════════════════╗\n"
            "║                  WIZ ERROR                   ║\n"
            "╚══════════════════════════════════════════════╝"
        )

        if self.line is None:
            return (
                f"{banner}\n\n"
                f"Message : {self.message}\n"
            )

        return (
            f"{banner}\n\n"
            f"Location : Line {self.line}, Column {self.column}\n"
            f"Message  : {self.message}\n"
        )


class WizSyntaxError(WizError):
    pass

class WizRuntimeError(WizError):
    pass

class WizTypeError(WizError):
    pass

class WizNameError(WizError):
    pass

class WizMemberError(WizError):
    pass

class WizIndexError(WizError):
    pass

class WizKeyError(WizError):
    pass

class WizVariableNotImmutable(WizError):
    pass

class WizVariableDeclared(WizError):
    pass

class WizParameterError(WizError):
    pass