from pydantic import BaseModel

class ScheduleResponse(BaseModel):
    quiz_id: int
    selected_ids: list[int]

class TagResponse(BaseModel):
    quiz_id: int
    selected_ids: list[int]

class ActivityResponse(BaseModel):
    quiz_id: int
    accepted_ids: list[int]
    rejected_ids: list[int]
