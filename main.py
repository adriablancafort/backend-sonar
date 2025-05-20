from database import supabase
from models import ScheduleRequest, TagRequest, ActivityRequest, SwipeRequest
from functions import activities_swipes, activities_results, activities_final_tags
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

@app.post("/quiz")
def create_quiz():
    """Create a new quiz row and return its ID."""
    response = supabase.table("quizzes").insert({}).execute()
    return {"quiz_id": response.data[0]['id']}


@app.get("/schedule")
def read_schedule():
    """Fetch all schedule from the database."""
    response = supabase.table("schedules").select("id,title,date,type").execute()
    return response.data

@app.post("/schedule")
def write_schedule(quiz_id: int, request: ScheduleRequest):
    """Write selected schedule IDs to the database."""
    supabase.table("quizzes").update({
        "schedule_ids": request.selected_ids
    }).eq("id", quiz_id).execute()
    return {"status": "success"}


@app.get("/tags")
def read_tags():
    """Fetch all tags from the database."""
    response = supabase.table("tags").select("id,title,image_uri").execute()
    return response.data

@app.post("/tags")
def write_tags(quiz_id: int, request: TagRequest):
    """Write selected tag IDs to the database."""
    supabase.table("quizzes").update({
        "tags_ids": request.selected_ids
    }).eq("id", quiz_id).execute()
    return {"status": "success"}


@app.get("/activities")
def read_activities(quiz_id: int):
    """Return activities filtered by quiz's selected schedules."""
    response = supabase.table("quizzes").select("schedule_ids").eq("id", quiz_id).single().execute()
    
    schedule_ids = [int(id_str) for id_str in response.data["schedule_ids"].strip("[]").split(",") if id_str.strip()]

    response = supabase.table("activities").select("id,title,image_uri").in_("schedule_id", schedule_ids).execute()
    return response.data

@app.post("/activities")
def read_activities(quiz_id: int, request: ActivityRequest):
    """Write essential activities IDs to the database."""
    supabase.table("quizzes").update({
        "essential_activities_ids": request.selected_ids
    }).eq("id", quiz_id).execute()
    return {"status": "success"}


@app.get("/swipes")
def read_activities(quiz_id: int):
    """Return personalized swipes list."""
    response = activities_swipes(quiz_id)
    return response

@app.post("/swipes")
def write_activities(quiz_id: int, request: SwipeRequest):
    """Write accepted and rejected swipes IDs to the database."""
    supabase.table("quizzes").update({
        "accepted_activities_ids": request.accepted_ids,
        "rejected_activities_ids": request.rejected_ids
    }).eq("id", quiz_id).execute()
    return {"status": "success"}


@app.get("/results")
def read_results(quiz_id: int):
    """Return the final personalized schedule results."""
    response = activities_results(quiz_id)
    return response

@app.get("/personalized-tags")
def read_personalized_tags(quiz_id: int):
    """Return the final personalized tags results."""
    response = activities_final_tags(quiz_id)
    return response
