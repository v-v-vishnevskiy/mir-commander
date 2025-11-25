from pydantic import Field

from mir_commander.api.program import ProgramConfig, WindowSizeConfig


class Config(ProgramConfig):
    window_size: WindowSizeConfig = WindowSizeConfig(min_width=325, min_height=220, width=350, height=300)
    decimals: int = Field(default=6, ge=1, le=15, description="Number of decimal places to display")
