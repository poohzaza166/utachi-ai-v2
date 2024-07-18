from typing import List, Any, Union, Optional, Dict, Literal
from pydantic import BaseModel
from pydantic.dataclasses import dataclass

@dataclass
class User(BaseModel):
    Username: str
    info: str
    permission: Literal["admin", "user", "api"]
    api_token: Optional[str]
    passwd: str
    conv_db: dict
    conv_vector: Any
    config: dict
    api_key: Optional[str]

