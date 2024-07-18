class FunctionCallSyntaxError(Exception):
    """This is a function call error """
    def __init__(self, *args: object) -> None:
        super().__init__("malform function call or incomplete function call")

class ParsingError(Exception):
    """This is a syntax parsing error"""
    def __init__(self, *args: object) -> None:
        super().__init__(*args)

class NoFunctionFoundError(Exception):
    """No functions found in the completion. or something went wrong druing functioncall"""
    def __init__(self, *args: object) -> None:
        super().__init__("No functions found in the completion. or something went wrong druing functioncall")

class MalFormAnswerContainingFunctioncall(Exception):
    """The program detected functioncalling string inside post process message"""
    def __init__(self, *args: object) -> None:
        super().__init__("The program detected functioncalling string inside post process message", *args)