class FunctionCallSyntaxError(Exception):
    """This is a function call error """
    def __init__(self, *args: object) -> None:
        super().__init__("malform function call or incomplete function call")

class ParsingError(Exception):
    """This is a syntax parsing error"""
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


    