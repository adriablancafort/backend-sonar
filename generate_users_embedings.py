from database import supabase
from embedings import get_embedding

results = supabase.table("users").select("id,description").execute()

for user in results.data:
    user_text = user['description']
    embedding = get_embedding(user_text)
    supabase.table("users").update({"embedding": embedding}).eq("id", user["id"]).execute()