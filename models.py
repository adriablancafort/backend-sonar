from pydantic import BaseModel

class ScheduleRequest(BaseModel):
    selected_ids: list[int]

class TagRequest(BaseModel):
    selected_ids: list[int]

class ActivityRequest(BaseModel):
    selected_ids: list[int]

class SwipeRequest(BaseModel):
    accepted_ids: list[int]
    rejected_ids: list[int]
