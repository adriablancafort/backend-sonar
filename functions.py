from database import supabase

def activities_swipes(quiz_id: int):
    """Return personalized activities swipes list based on tag embeddings similarity."""

    results = supabase.rpc(
        "get_matching_activities_by_quiz_tags",
        {
            "input_quiz_id": quiz_id,
            "match_count": 8
        }
    ).execute()
    
    return results.data

def activities_results(quiz_id: int):
    """Return the final personalized schedule results."""
    
    results = supabase.rpc(
        "get_activities_by_user_preferences",
        {
            "input_quiz_id": quiz_id,
        }
    ).execute()

    ids = optimum_timetable(results.data)

    results = supabase.table("activities").select("id,title,description,image_uri,start_time,end_time,schedules(title)").in_("id", ids).execute()
    
    return results.data

def optimum_timetable(input):
    ids = [1, 4, 10, 22]
    return ids
