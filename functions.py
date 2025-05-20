from database import supabase
from datetime import time, datetime
from intervaltree import IntervalTree
from collections import defaultdict
import random

def get_swipes(quiz_id: int, return_count: int = 8, match_count: int = 20):
    """Return personalized activities swipes list based on tag embeddings similarity."""

    response = supabase.rpc(
        "swipes_query",
        {
            "input_quiz_id": quiz_id,
            "match_count": match_count
        }
    ).execute().data

    # Return random selection of activities of length return_count
    selected = random.sample(range(len(response)), return_count)
    selected.sort()
    selected = [results[idx]["id"] for idx in selected]

    results = supabase.table("activities").select("id,title,description,image_uri,start_time,end_time,video_uri,tags,activity_uri,dominant_color,dark_color,pastel_color,schedules(title)").in_("id", selected).execute()
    return results.data


def get_results(quiz_id: int):
    """Return the final personalized schedule results."""
    
    response = supabase.rpc(
        "results_query",
        {
            "input_quiz_id": quiz_id,
        }
    ).execute()

    ids = optimum_timetable(response.data)

    # Store results ids
    supabase.table("quizzes").update({
        "results_ids": ids
    }).eq("id", quiz_id).execute()

    activities = supabase.table("activities").select("id,title,description,image_uri,start_time,end_time,tags,dominant_color,dark_color,pastel_color,activity_uri,schedules(title)").in_("id", ids).execute()

    # Sort results by the order of ids
    ids_order = {id: i for i, id in enumerate(ids)}
    results = sorted(activities.data, key=lambda item: ids_order[item["id"]])
    return results


def get_recap(quiz_id: int):
    """Return the final personalized tags results."""

    response = supabase.rpc(
        "recap_query",
        {
            "input_quiz_id": quiz_id
        }
    ).execute()

    data = response.data
    if not data or len(data) < 250:
        return []

    last_distance = data[-1]["distance"]
    selected = [
        (data[random.randint(0, 10)]["tag_id"], (1 - (data[random.randint(0, 10)]["distance"] / last_distance)) * 100),
        (data[random.randint(60, 140)]["tag_id"], (1 - (data[random.randint(60, 140)]["distance"] / last_distance)) * 100),
        (data[random.randint(180, 250)]["tag_id"], (1 - (data[random.randint(180, 250)]["distance"] / last_distance)) * 100)
    ]

    ordered_ids = [tag_id for tag_id, _ in selected]
    ids_order = {tag_id: i for i, (tag_id, _) in enumerate(selected)}
    id_to_percentage = {tag_id: round(p, 2) for tag_id, p in selected}

    tags_response = supabase.table("all_tags").select("id,title,frase").in_("id", ordered_ids).execute()

    enriched = []
    for tag in tags_response.data:
        tag["percentage"] = id_to_percentage[tag["id"]]
        enriched.append(tag)

    results = sorted(enriched, key=lambda t: ids_order[t["id"]])
    return results


def optimum_timetable(input_activities: list[dict]) -> list[int]:
    """Given a list of activities sorted by priority (essential first),
    finds a maximal length scheduling."""

    trees = defaultdict(IntervalTree) # One IntervalTree per schedule_id

    # input_activities is already sorted by the SQL query:
    # 1. Essential activities
    # 2. Other activities, ranked by preference.
    # This loop will try to place essential activities first.
    for act in input_activities:
        start = time_to_minutes(act["start_time"])
        end = time_to_minutes(act["end_time"])

        tree = trees[act["schedule_id"]]
        if not tree.overlaps(start, end):
            tree[start:end] = act["id"]

    # Sort schedules by ID for consistent output order of schedules
    trees = dict(sorted(trees.items()))

    selected_ids = []
    for schedule_id in sorted(trees.keys()): # Process schedules in a consistent order
        tree = trees[schedule_id]
        intervals = sorted(tree, key=lambda i: i.begin) # Sort activities within each schedule by start time
        selected_ids.extend(i.data for i in intervals)
            
    return selected_ids


def time_to_minutes(t: time) -> int:
    """Converts time to minutes."""

    t = datetime.strptime(t, "%H:%M:%S").time()
    if t.hour < 8: # Because Sónar Night has activities before and past 24h, 8h is the middle bewtween start of Sònar Day and end of Sònar Night
        return t.hour + 24 + t.minute + 24 * 60
    return t.hour * 60 + t.minute
