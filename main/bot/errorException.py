class FunctionCallSyntaxError(Exception):
    """This is a function call error """
    def __init__(self, *args: object) -> None:
        super().__init__(*args)

    