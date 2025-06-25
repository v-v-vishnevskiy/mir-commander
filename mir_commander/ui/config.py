from typing import Callable

from pydantic import BaseModel, Field


class ApplyCallbacks(BaseModel):
    functions: list[Callable] = Field(
        default_factory=list, 
        description="List of functions to call when applying config changes"
    )

    def add(self, fn: Callable):
        """Add a function to the list of apply callbacks."""
        self.functions.append(fn)
    
    def run(self):
        """Run all registered apply callbacks."""
        for fn in self.functions:
            fn()
