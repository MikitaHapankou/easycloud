from pydantic import BaseModel
from typing import List, Dict

class dashboardFileList(BaseModel):
    username: str
    files: List[Dict[str, str]]
