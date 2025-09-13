from pydantic import BaseModel, model_validator, Field
import us
from datetime import datetime

US_STATES_ABBR = [state.abbr for state in us.states.STATES]


class MedianSaleRequest(BaseModel):
    city: str
    state: str = Field(
        description="The state of the city",
        examples=US_STATES_ABBR,
        json_schema_extra={"enum": US_STATES_ABBR},
    )

    @model_validator(mode="after")
    def validate_state(self):
        if self.state not in US_STATES_ABBR:
            raise ValueError(
                f"Invalid state: {self.state}, allowed states: {US_STATES_ABBR}"
            )
        return self


class MedianScrapeOutput(BaseModel):
    date: datetime
    regionName: str
    value: float
