from main.bot.lib.tools import BaseTool
from pydantic import Field, validator
from typing import List, Optional  
from  pyowm import OWM

class Weather(BaseTool):
    """Use To get the weather of a location."""

    location: str = Field(description="The location to get the weather of.")

    @validator('location')
    def location_must_not_be_empty(cls, v):
        if not v:
            raise ValueError("Location cannot be empty.")
        return v

    def run(self, location: str) -> str:
        """Use the tool."""
        owm = OWM('f9e5c4f9d1d4e8b1e8f3e6e2b7e5d4e1')
        mgr = owm.weather_manager()
        observation = mgr.weather_at_place(location)
        print(observation)
        w = observation.weather
        print(w) 
        return w.detailed_status
    