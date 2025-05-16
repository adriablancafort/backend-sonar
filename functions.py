from database import supabase
from datetime import time, datetime
from intervaltree import IntervalTree
from collections import defaultdict
import random
import numpy as np

def activities_swipes(quiz_id: int, return_count: int = 6,
                      match_count: int = 20, roulette=False):
    """Return personalized activities swipes list based on tag embeddings similarity."""

    match_count = max(return_count, match_count)

    results = supabase.rpc(
        "validation_get_matching_activities_by_quiz_tags",
        {
            "input_quiz_id": quiz_id,
            "match_count": match_count
        }
    ).execute().data

    if roulette:
        # roulette random selection

        indexes = np.array(range(len(results)))
        weights = np.array(range(len(results), 0, -1))

        selected = []

        for _ in range(return_count):
            prob = weights / weights.sum()
            
            idx = np.random.choice(len(indexes), p=prob)
            selected.append(indexes[idx])

            indexes = np.delete(indexes, idx)
            weights = np.delete(weights, idx)
        
        selected.sort()
        selected = [results[idx]["id"] for idx in selected]

        results = supabase.table("activities").select("id,title,description,image_uri,start_time,end_time,video_uri,tags,activity_uri,dominant_color,dark_color,pastel_color,schedules(title)").in_("id", selected).execute()

        return results.data
    else:
        # uniform random selection
        selected = random.sample(range(len(results)), return_count)
        
        selected.sort()
        selected = [results[idx]["id"] for idx in selected]

        results = supabase.table("activities").select("id,title,description,image_uri,start_time,end_time,video_uri,tags,activity_uri,dominant_color,dark_color,pastel_color,schedules(title)").in_("id", selected).execute()

        return results.data


def activities_results(quiz_id: int):
    """Return the final personalized schedule results."""
    
    results = supabase.rpc(
        "validation_get_activities_by_user_preferences",
        {
            "input_quiz_id": quiz_id,
        }
    ).execute()

    ids = optimum_timetable(results.data)
    
    ids_order = {id: i for i, id in enumerate(ids)} #In order to maintain the order of the activities

    results = supabase.table("activities").select("id,title,description,image_uri,start_time,end_time,tags,dominant_color,dark_color,pastel_color,activity_uri,schedules(title)").in_("id", ids).execute()

    results = sorted(results.data, key=lambda item: ids_order[item["id"]])

    return results


def activities_final_tags(quiz_id: int):
    """Return the final personalized tags results."""

    results = supabase.rpc(
        "validation_get_tag_distances_by_user_preferences",
        {
            "input_quiz_id": quiz_id,
        }
    ).execute()

    ids_with_distances = personalized_tags(results.data)

    ordered_ids = [id for id, _ in ids_with_distances]
    ids_order = {id: i for i, (id, _) in enumerate(ids_with_distances)}
    id_to_percentatge = {id: round(percentatge, 2) for id, percentatge in ids_with_distances}

    results = supabase.table("all_tags").select("id,title").in_("id", ordered_ids).execute()

    enriched = []
    for item in results.data:
        item["percentage"] = id_to_percentatge[item["id"]]
        enriched.append(item)

    enriched = sorted(enriched, key=lambda item: ids_order[item["id"]])

    return enriched



def personalized_tags(input: list[dict]) -> list[tuple[int]]:
    """
    Given a list of ids and distances, sorted by priority 
    descendingly, returns three random tags and their matching
    percentages. 

    Running time: O(1)

    Params:
        input: list of tuples (id, distance). Each tuple must have the fields
                "id" (int), "distance" (float)
    
    Returns:
        list: list of tuples (id, distance). Each tuple must have the fields
                "id" (int), "distance" (float)
    """

    first = random.randint(0, 10)
    first_tag, first_percentage = input[first]["tag_id"], (1-(input[first]["distance"]/input[-1]["distance"]))*100

    second = random.randint(60, 140)
    second_tag, second_percentage = input[second]["tag_id"], (1-(input[second]["distance"]/input[-1]["distance"]))*100

    third = random.randint(180, 250)
    third_tag, third_percentage = input[third]["tag_id"], (1-(input[third]["distance"]/input[-1]["distance"]))*100

    return [
        (first_tag, first_percentage),
        (second_tag, second_percentage),
        (third_tag, third_percentage)
    ]


def time_to_minutes(t: time) -> int:
    """
    Converts time to minutes.
    """
    t = datetime.strptime(t, "%H:%M:%S").time()
    if t.hour < 8:   #Because Sónar Night has activities before and past 24h, 8h is the middle bewtween start of Sònar Day and end of Sònar Night
        return t.hour + 24 + t.minute + 24 * 60
    return t.hour * 60 + t.minute

def optimum_timetable(input: list[dict]) -> list[int]:
    """
    Given a list of activities sorted by priority
    descendingly, finds a maximal length scheduling so 
    that no activity is chosen unless its choosing 
    doesn't impede a higher priority activity from being selected.

    Running time: O(n·log(n))

    Params:
        input: list of activities. Each activity must have the fields
                "id" (int), schedule_id (int), "start_time" (str, e.g '17:00:00') 
                and "end_time" (str)
    
    Returns:
        list: ids of the selected activities
    """
    trees = defaultdict(IntervalTree)  # IntervalTree per cada schedule_id

    for act in input:
        start = time_to_minutes(act["start_time"])
        end = time_to_minutes(act["end_time"])

        tree = trees[act["schedule_id"]]
        if not tree.overlaps(start, end):
            tree[start:end] = act["id"]
    
    trees = dict(sorted(trees.items()))     #beacuse input is not sorted by schedule_id
    
    ordered_ids = []
    for tree in trees.values():  # o simplement: for tree in trees.values() si l'ordre dels schedules no importa
        intervals = sorted(tree, key=lambda i: i.begin)
        ordered_ids += [i.data for i in intervals]

    return ordered_ids

 



def weighted_scheduling(activities: list[dict])->list[int]:
    """
    Given a set of activities, returns the subset of non-overlapping 
    activities with maximum summed value.

    Running time: O(n·log(n))

    Params:
        activities: list of activities. Each activity must have the fields
               "id" (int), "start_time" (int), "end_time" (int) 
               and value (int or float)

    Returns:
        list: ids of the selected activities
    """
    n = len(activities)

    # sort ascendingly by end time
    activities.sort(key=lambda x: x["end_time"])

    # stores the maximum value achievable with the first "i" activities
    dp_table = [-1 for _ in range(len(activities))]
    # the following recurrence applies: 
    #   dp_table[i] = max(dp_table[i-1], value(i)+dp_table[prev(i)]
    # where value(i) = value of ith activity, prev(i) = 
    # index of the first previous activity i-1,i-2,i-3,... that 
    # doesn't overlap with activity "i"

    for i in range(n):
        p = prev(activities, i)
        dp_table[i] = max(dp_table[i - 1], activities[i]['value'] + \
                          (dp_table[p] if p >= 0 else 0))
        
    # backtrack across the dp table to find the events that were selected
    ids = []
    i = n - 1
    while i >= 0:
        if i == 0 or dp_table[i] != dp_table[i - 1]:
            ids.append(activities[i]["id"])
            i = prev(activities, i)
        else: i -= 1
            

    return ids

def prev(activities: list[dict], i: int)->int:
    """
    Returns the index of the first previous activity that
    doesn't overlap with activity "i".

    Params:
        activities: list of activities, sorted ascendingly by
                    end time
        i: index of the current activity
    
    Returns:
        int: index of the previous activity, if it exists, else -1

    Running time: log(n) (binary search)
    """
    start_time = activities[i]["start_time"]

    l, r = 0, i - 1
    best_idx = -1

    while l <= r:
        mid = (l + r) // 2
        if activities[mid]["end_time"] <= start_time:
            best_idx = mid
            l = mid + 1
        else:
            r = mid - 1

    return best_idx
