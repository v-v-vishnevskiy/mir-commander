from typing import Literal

from pydantic import BaseModel


class Unex(BaseModel):
    data_type: Literal["unex"] = "unex"
