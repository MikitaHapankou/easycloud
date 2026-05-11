from pydantic import BaseModel

class DashboardFileResponse(BaseModel):
    filenames: list[str]