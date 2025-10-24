from pydantic import BaseModel


class TimeframeDetectionResponse(BaseModel):
    timeframe_specified: bool
    start_date: str | None
    end_date: str | None
