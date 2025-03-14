from database import supabase
from fastapi import FastAPI

app = FastAPI()

@app.get("/activities")
def read_activities():
    results = supabase.table("activities").select("title,description,video_uri").execute()
    return results.data