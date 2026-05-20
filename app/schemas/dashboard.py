from pydantic import BaseModel
from typing import List

class dashboardFileList(BaseModel):
    username: str
    files: List[str]
