from database import supabase
from models import ActivitySwipe
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/activities")
def read_activities():
    ids = [1, 2]
    results = supabase.table("activities").select("id,title,description,video_uri").in_("id", ids).execute()
    return results.data

@app.post("/activities")
def process_activity_swipe(swipes: list[ActivitySwipe]):
    for swipe in swipes:
        print(f"Activity ID: {swipe.id}, Swiped Right: {swipe.swipe_right}")
    return {"status": "success"}