from database import supabase
from embedings import get_embedding

ids = [1]

results = supabase.table("activities").select("id,title,description").in_("id", ids).execute()

for activity in results.data:
    activity_text = f"{activity['title']}. {activity['description']}"
    
    embedding = get_embedding(activity_text)
    
    supabase.table("activities").update({"embedding": embedding}).eq("id", activity["id"]).execute()
    print(f"Embedding stored for {activity['title']}")