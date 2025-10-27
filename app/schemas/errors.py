from pydantic import BaseModel
from typing import Optional, Union

class ErrorResponse(BaseModel):
    error: str
    details: Optional[Union[str, dict, list]] = None
