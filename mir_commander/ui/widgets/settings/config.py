from pydantic import BaseModel, Field


class SettingsConfig(BaseModel):
    current_page: int = 0
    current_tab: int = 0
    pos: None | list[int] = Field(default=None, min_length=2, max_length=2, description="x, y coordinates")
    size: None | list[int] = Field(default=None, min_length=2, max_length=2, description="width, height")
