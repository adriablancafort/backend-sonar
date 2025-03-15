from pydantic import BaseModel

class ActivitySwipe(BaseModel):
    id: int
    swipe_right: bool