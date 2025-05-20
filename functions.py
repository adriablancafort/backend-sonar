from database import supabase
from datetime import time, datetime
from intervaltree import IntervalTree
from collections import defaultdict
import random

def get_swipes(quiz_id: int, return_count: int = 8, match_count: int = 20):
    """Return personalized activities swipes list based on tag embeddings similarity."""

    match_count = max(return_count, match_count)

    results = supabase.rpc(
        "swipes_query",
        {
            "input_quiz_id": quiz_id,
            "match_count": match_count
        }
    ).execute().data

    # Return random selection of activities of length return_count
    selected = random.sample(range(len(results)), return_count)
    selected.sort()
    selected = [results[idx]["id"] for idx in selected]

    results = supabase.table("activities").select("id,title,description,image_uri,start_time,end_time,video_uri,tags,activity_uri,dominant_color,dark_color,pastel_color,schedules(title)").in_("id", selected).execute()
    return results.data


def get_results(quiz_id: int):
    """Return the final personalized schedule results."""
    
    results = supabase.rpc(
        "results_query",
        {
            "input_quiz_id": quiz_id,
        }
    ).execute()

    ids = optimum_timetable(results.data)
    
    activities = supabase.table("activities").select("id,title,description,image_uri,start_time,end_time,tags,dominant_color,dark_color,pastel_color,activity_uri,schedules(title)").in_("id", ids).execute()

    # Sort results by the order of ids
    ids_order = {id: i for i, id in enumerate(ids)}
    results = sorted(activities.data, key=lambda item: ids_order[item["id"]])
    return results


def get_recap(quiz_id: int):
    """Return the final personalized tags results."""

    # Fetch raw tag distances from Supabase
    response = supabase.rpc(
        "recap_query",
        {"input_quiz_id": quiz_id}
    ).execute()

    data = response.data
    if not data or len(data) < 250:
        return []

    # Pick 3 tags with custom random logic
    last_distance = data[-1]["distance"]
    selected = [
        (data[random.randint(0, 10)]["tag_id"], (1 - (data[random.randint(0, 10)]["distance"] / last_distance)) * 100),
        (data[random.randint(60, 140)]["tag_id"], (1 - (data[random.randint(60, 140)]["distance"] / last_distance)) * 100),
        (data[random.randint(180, 250)]["tag_id"], (1 - (data[random.randint(180, 250)]["distance"] / last_distance)) * 100)
    ]

    # Structure IDs, ordering, and percentage mapping
    ordered_ids = [tag_id for tag_id, _ in selected]
    ids_order = {tag_id: i for i, (tag_id, _) in enumerate(selected)}
    id_to_percentage = {tag_id: round(p, 2) for tag_id, p in selected}

    # Fetch tag details
    tags_response = supabase.table("all_tags").select("id,title,frase").in_("id", ordered_ids).execute()

    # Enrich and sort
    enriched = []
    for tag in tags_response.data:
        tag["percentage"] = id_to_percentage[tag["id"]]
        enriched.append(tag)

    results = sorted(enriched, key=lambda t: ids_order[t["id"]])
    return results


def optimum_timetable(input: list[dict]) -> list[int]:
    """Given a list of activities sorted by priority descendingly, finds a maximal length scheduling so 
    that no activity is chosen unless its choosing doesn't impede a higher priority activity from being selected."""

    trees = defaultdict(IntervalTree) # One IntervalTree per schedule_id

    for act in input:
        start = time_to_minutes(act["start_time"])
        end = time_to_minutes(act["end_time"])

        tree = trees[act["schedule_id"]]
        if not tree.overlaps(start, end):
            tree[start:end] = act["id"]

    # Sort schedules by ID (optional unless ordering matters)
    trees = dict(sorted(trees.items()))

    selected_ids = []
    for tree in trees.values():
        intervals = sorted(tree, key=lambda i: i.begin)
        selected_ids.extend(i.data for i in intervals)

    return selected_ids


def time_to_minutes(t: time) -> int:
    """Converts time to minutes."""

    t = datetime.strptime(t, "%H:%M:%S").time()
    if t.hour < 8: # Because Sónar Night has activities before and past 24h, 8h is the middle bewtween start of Sònar Day and end of Sònar Night
        return t.hour + 24 + t.minute + 24 * 60
    return t.hour * 60 + t.minute
