from database import supabase
from models import ScheduleResponse, TagResponse, ActivityResponse
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

@app.get("/quiz")
def create_quiz():
    """Create a new quiz row and return its ID."""
    response = supabase.table("quizzes").insert({}).execute()
    return {"quiz_id": response.data[0]['id']}


@app.get("/schedule")
def read_schedule():
    """Fetch all schedules from the database."""
    results = supabase.table("schedules").select("id,title,date").execute()
    return results.data

@app.post("/schedule")
def write_schedule(response: ScheduleResponse):
    """Write selected schedule IDs to the database."""
    supabase.table("quizzes").update({
        "schedule_ids": response.selected_ids
    }).eq("id", response.quiz_id).execute()
    return {"status": "success"}


@app.get("/tags")
def read_tags():
    """Fetch all tags from the database."""
    results = supabase.table("tags").select("id,title").execute()
    return results.data

@app.post("/tags")
def write_tags(response: TagResponse):
    """Write selected tag IDs to the database."""
    supabase.table("quizzes").update({
        "tags_ids": response.selected_ids
    }).eq("id", response.quiz_id).execute()
    return {"status": "success"}


@app.get("/activities")
def read_activities():
    """Return personalized activities list."""
    ids = [1, 4, 10, 23]
    results = supabase.table("activities").select("id,title,description,video_uri").in_("id", ids).execute()
    return results.data

@app.post("/activities")
def write_activities(response: ActivityResponse):
    """Write accepted and rejected activity IDs to the database."""
    print(response)
    supabase.table("quizzes").update({
        "accepted_activities_ids": response.accepted_ids,
        "rejected_activities_ids": response.rejected_ids
    }).eq("id", response.quiz_id).execute()
    return {"status": "success"}


@app.get("/results")
def read_results():
    """Return the final personalized schedule results."""
    results = [
        {
            "title": "Yoga Class",
            "description": "A relaxing yoga session to improve flexibility and reduce stress.",
            "schedule": "Monday, 7:00 AM - 8:00 AM",
        },
        {
            "title": "Cooking Workshop",
            "description": "Learn to cook delicious meals with professional chefs.",
            "schedule": "Wednesday, 5:00 PM - 7:00 PM",
        },
        {
            "title": "Art Class",
            "description": "Explore your creativity with painting and drawing lessons.",
            "schedule": "Friday, 3:00 PM - 5:00 PM",
        },
        {
            "title": "Fitness Bootcamp",
            "description": "An intense workout session to boost your strength and stamina.",
            "schedule": "Saturday, 6:00 AM - 7:30 AM",
        },
    ]
    return results
