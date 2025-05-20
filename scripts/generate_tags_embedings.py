from database import supabase
from ai import get_embedding

results = supabase.table("tags").select("id,title,long_text").execute()

for tag in results.data:
    tag_text = f"{tag['title']}. {tag['long_text']}"
    embedding = get_embedding(tag_text)
    supabase.table("tags").update({"embedding": embedding}).eq("id", tag["id"]).execute()