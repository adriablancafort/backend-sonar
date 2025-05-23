CREATE OR REPLACE FUNCTION results_query(input_quiz_id INTEGER)
RETURNS TABLE (id INTEGER, start_time TIME, end_time TIME, schedule_id INTEGER)
LANGUAGE plpgsql
AS $$
DECLARE
    accepted_ids INTEGER[];
    rejected_ids INTEGER[];
    schedule_ids INTEGER[];
    essential_ids INTEGER[];
    accepted_embedding VECTOR;
    rejected_embedding VECTOR;
BEGIN
    -- Get the accepted_activities_ids, rejected_activities_ids, schedule_ids, and essential_activities_ids from the quiz
    SELECT 
        COALESCE( (CASE WHEN trim(both '[]' from q.accepted_activities_ids) = '' THEN ARRAY[]::INTEGER[] ELSE string_to_array(trim(both '[]' from q.accepted_activities_ids), ',')::INTEGER[] END), ARRAY[]::INTEGER[] ),
        COALESCE( (CASE WHEN trim(both '[]' from q.rejected_activities_ids) = '' THEN ARRAY[]::INTEGER[] ELSE string_to_array(trim(both '[]' from q.rejected_activities_ids), ',')::INTEGER[] END), ARRAY[]::INTEGER[] ),
        CASE
            WHEN q.schedule_ids IS NULL THEN NULL::INTEGER[]
            WHEN trim(both '[]' from q.schedule_ids) = '' THEN ARRAY[]::INTEGER[]
            ELSE string_to_array(trim(both '[]' from q.schedule_ids), ',')::INTEGER[]
        END,
        COALESCE( (CASE WHEN trim(both '[]' from q.essential_activities_ids) = '' THEN ARRAY[]::INTEGER[] ELSE string_to_array(trim(both '[]' from q.essential_activities_ids), ',')::INTEGER[] END), ARRAY[]::INTEGER[] )
    INTO 
        accepted_ids,
        rejected_ids,
        schedule_ids,
        essential_ids
    FROM quizzes q
    WHERE q.id = input_quiz_id;
    
    -- Check if quiz exists or has valid schedule_ids
    IF schedule_ids IS NULL OR cardinality(schedule_ids) = 0 THEN
        RAISE EXCEPTION 'Quiz with ID % not found or has no schedule_ids', input_quiz_id;
    END IF;
    
    -- Calculate average embedding of accepted activities (if any)
    IF cardinality(accepted_ids) > 0 THEN
        SELECT AVG(a.embedding) INTO accepted_embedding
        FROM activities a
        WHERE a.id = ANY(accepted_ids);
    END IF;
    
    -- Calculate average embedding of rejected activities (if any)
    IF cardinality(rejected_ids) > 0 THEN
        SELECT AVG(a.embedding) INTO rejected_embedding
        FROM activities a
        WHERE a.id = ANY(rejected_ids);
    END IF;
    
    -- Return activities ranked by preference
    -- If we have both accepted and rejected activities:
    IF accepted_embedding IS NOT NULL AND rejected_embedding IS NOT NULL THEN
        RETURN QUERY
        SELECT res.id, res.start_time, res.end_time, res.schedule_id
        FROM (
            SELECT
                a.id::INTEGER, a.start_time::TIME, a.end_time::TIME, a.schedule_id::INTEGER,
                a.embedding AS activity_embedding, 0 AS sort_priority
            FROM activities a
            WHERE a.id = ANY(essential_ids) AND a.schedule_id = ANY(schedule_ids)
            UNION ALL
            SELECT
                a.id::INTEGER, a.start_time::TIME, a.end_time::TIME, a.schedule_id::INTEGER,
                a.embedding AS activity_embedding, 1 AS sort_priority
            FROM activities a
            WHERE 
                a.schedule_id = ANY(schedule_ids) AND
                NOT (a.id = ANY(essential_ids)) AND
                NOT (a.id = ANY(rejected_ids))
        ) AS res
        ORDER BY 
            res.sort_priority ASC,
            (-(res.activity_embedding <=> accepted_embedding) + (res.activity_embedding <=> rejected_embedding)) DESC;
    
    -- If we only have accepted activities:
    ELSIF accepted_embedding IS NOT NULL THEN
        RETURN QUERY
        SELECT res.id, res.start_time, res.end_time, res.schedule_id
        FROM (
            SELECT
                a.id::INTEGER, a.start_time::TIME, a.end_time::TIME, a.schedule_id::INTEGER,
                a.embedding AS activity_embedding, 0 AS sort_priority
            FROM activities a
            WHERE a.id = ANY(essential_ids) AND a.schedule_id = ANY(schedule_ids)
            UNION ALL
            SELECT 
                a.id::INTEGER, a.start_time::TIME, a.end_time::TIME, a.schedule_id::INTEGER,
                a.embedding AS activity_embedding, 1 AS sort_priority
            FROM activities a
            WHERE 
                a.schedule_id = ANY(schedule_ids) AND
                NOT (a.id = ANY(essential_ids))
        ) AS res
        ORDER BY 
            res.sort_priority ASC,
            res.activity_embedding <=> accepted_embedding ASC;
    
    -- If we only have rejected activities (or neither accepted nor rejected):
    ELSE
        RETURN QUERY
        SELECT res.id, res.start_time, res.end_time, res.schedule_id
        FROM (
            SELECT
                a.id::INTEGER, a.start_time::TIME, a.end_time::TIME, a.schedule_id::INTEGER,
                a.embedding AS activity_embedding, 0 AS sort_priority
            FROM activities a
            WHERE a.id = ANY(essential_ids) AND a.schedule_id = ANY(schedule_ids)
            UNION ALL
            SELECT 
                a.id::INTEGER, a.start_time::TIME, a.end_time::TIME, a.schedule_id::INTEGER,
                a.embedding AS activity_embedding, 1 AS sort_priority
            FROM activities a
            WHERE 
                a.schedule_id = ANY(schedule_ids) AND
                NOT (a.id = ANY(essential_ids)) AND
                NOT (a.id = ANY(rejected_ids))
        ) AS res
        ORDER BY 
            res.sort_priority ASC,
            CASE 
                WHEN rejected_embedding IS NOT NULL THEN (res.activity_embedding <=> rejected_embedding) 
                ELSE NULL -- Or some other default sorting if rejected_embedding is NULL
            END DESC;
    END IF;
END;
$$;
