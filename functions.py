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

def optimum_timetable(input: list[dict]) -> list[int]:
    """
    Given a list of activities sorted by priority
    descendingly, finds a maximal length scheduling so 
    that no activity is chosen unless its choosing 
    doesn't impede a higher priority activity from being seleced.

    The problem can be reduced to a weighted scheduling with
    power of 2 weights.

    Running time: O(n·log(n))

    Params:
        input: list of activities. Each activity must have the fields
               "id" (int), "start_time" (str, e.g '17:00:00') 
               and "end_time" (str)
    
    Returns:
        list: ids of the selected activities
    """
    
    # give power of 2 weights to the activities, so the
    # weighted scheduling becomes equivalent to a greedy
    # scheduling
    val = 1 << (len(input) - 1) # 2^(len(input) - 1)
    for i in range(len(input)):
        input[i]["value"] = val
        val = val // 2

    # convert time to integer
    for act in input:
        start, end = act["start_time"], act["end_time"]
        start_h, start_min, _ = map(int, start.split(':'))
        end_h, end_min, _ = map(int, end.split(':'))

        act["start_time"] = start_h * 60 + start_min
        act["end_time"] = end_h * 60 + end_min

    return weighted_scheduling(input)

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