from database import supabase

def activities_swipes(quiz_id: int):
    """Return personalized activities swipes list."""
    ids = [1, 4, 10, 22]
    results = supabase.table("activities").select("id,title,description,video_uri").in_("id", ids).execute()
    return results.data

def activities_results(quiz_id: int):
    """Return the final personalized schedule results."""
    ids = [1, 4, 10, 22]
    results = supabase.table("activities").select("id,title,description,image_uri,start_time,end_time,schedules(title)").in_("id", ids).execute()
    return results.data