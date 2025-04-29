from database import supabase
from embedings import get_embedding

results = supabase.table("activities").select("id,title,description,tags,long_text").execute()

for activity in results.data:
    activity_text = f"{activity['title']}. {activity['description']}. {activity['tags']} {activity['long_text']}"
    embedding = get_embedding(activity_text)
    supabase.table("activities").update({"embedding": embedding}).eq("id", activity["id"]).execute()
