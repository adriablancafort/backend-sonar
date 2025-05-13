CREATE OR REPLACE FUNCTION get_tag_distances_by_user_preferences(input_quiz_id INTEGER)
RETURNS TABLE(tag_id INTEGER, distance DOUBLE PRECISION)
LANGUAGE plpgsql
AS $$
DECLARE
    accepted_ids INTEGER[];
    rejected_ids INTEGER[];
    schedule_ids INTEGER[];
    accepted_embedding VECTOR;
    rejected_embedding VECTOR;
BEGIN
    -- Obtenir els vectors d'activitats acceptades/rebutjades i schedule_ids
    SELECT 
        string_to_array(trim(both '[]' from q.accepted_activities_ids), ',')::INTEGER[],
        string_to_array(trim(both '[]' from q.rejected_activities_ids), ',')::INTEGER[],
        string_to_array(trim(both '[]' from q.schedule_ids), ',')::INTEGER[]
    INTO 
        accepted_ids,
        rejected_ids,
        schedule_ids
    FROM quizzes q
    WHERE q.id = input_quiz_id;

    -- Check if quiz exists
    IF schedule_ids IS NULL THEN
        RAISE EXCEPTION 'Quiz with ID % not found', input_quiz_id;
    END IF;

    -- Calculate average embedding of accepted activities (if any)
    IF array_length(accepted_ids, 1) > 0 THEN
        SELECT AVG(a.embedding) INTO accepted_embedding
        FROM activities a
        WHERE a.id = ANY(accepted_ids);
    END IF;
    
    -- Calculate average embedding of rejected activities (if any)
    IF array_length(rejected_ids, 1) > 0 THEN
        SELECT AVG(a.embedding) INTO rejected_embedding
        FROM activities a
        WHERE a.id = ANY(rejected_ids);
    END IF;
    xgz
 -- Return activities ranked by preference
    -- If we have both accepted and rejected activities:
    IF accepted_embedding IS NOT NULL AND rejected_embedding IS NOT NULL THEN
        RETURN QUERY
        SELECT 
            a.id::INTEGER, 
            a.start_time::TIME, 
            a.end_time::TIME,
            a.schedule_id::INTEGER
        FROM activities a
        WHERE 
            a.schedule_id = ANY(schedule_ids) AND
            -- Exclude rejected activities
            NOT (a.id = ANY(rejected_ids))
        ORDER BY 
            -- Proximity to accepted minus proximity to rejected
            (-(a.embedding <=> accepted_embedding) + (a.embedding <=> rejected_embedding)) DESC;
    
    -- If we only have accepted activities:
    ELSIF accepted_embedding IS NOT NULL THEN
        RETURN QUERY
        SELECT 
            a.id::INTEGER,
            a.start_time::TIME, 
            a.end_time::TIME,
            a.schedule_id::INTEGER
        FROM activities a
        WHERE 
            a.schedule_id = ANY(schedule_ids)
        ORDER BY a.embedding <=> accepted_embedding ASC;
    
    -- If we only have rejected activities:
    ELSE
        RETURN QUERY
        SELECT 
            a.id::INTEGER,
            a.start_time::TIME, 
            a.end_time::TIME,
            a.schedule_id::INTEGER
        FROM activities a
        WHERE 
            a.schedule_id = ANY(schedule_ids) AND
            NOT (a.id = ANY(rejected_ids))
        ORDER BY a.embedding <=> rejected_embedding DESC; -- Sort by dissimilarity to rejected
    END IF;
END;
$$;
