from database import supabase
from models import ActivitySwipe
from fastapi import FastAPI

app = FastAPI()

@app.get("/activities")
def read_activities():
    results = supabase.table("activities").select("id,title,description,video_uri").execute()
    return results.data

@app.post("/activities")
def process_activity_swipe(swipes: list[ActivitySwipe]):
    for swipe in swipes:
        print(f"Activity ID: {swipe.id}, Swiped Right: {swipe.swipe_right}")
    return {"status": "success"}