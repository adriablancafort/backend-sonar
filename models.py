from pydantic import BaseModel

class ScheduleResponse(BaseModel):
    quiz_id: int
    selectedt: list[int]

class TagResponse(BaseModel):
    quiz_id: int
    selectedt: list[int]

class ActivityResponse(BaseModel):
    id: int
    selectedt: list[int]
