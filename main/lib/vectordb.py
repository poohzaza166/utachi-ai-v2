from typing import Callable, List, Optional, Literal, Tuple

class basedb:
    def __init__(self, embeding_model, ) -> None:
        self.embeding_model = embeding_model
        self.db