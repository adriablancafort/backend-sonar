CREATE OR REPLACE FUNCTION recap_query(input_quiz_id INTEGER)
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
    -- Get activity vectors from the quiz
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

    IF schedule_ids IS NULL THEN
        RAISE EXCEPTION 'Quiz with ID % not found', input_quiz_id;
    END IF;

    -- Calculate average embedding of accepted activities
    IF array_length(accepted_ids, 1) > 0 THEN
        SELECT AVG(a.embedding) INTO accepted_embedding
        FROM activities a
        WHERE a.id = ANY(accepted_ids);
    END IF;

    -- Calculate average embedding of rejected activities
    IF array_length(rejected_ids, 1) > 0 THEN
        SELECT AVG(a.embedding) INTO rejected_embedding
        FROM activities a
        WHERE a.id = ANY(rejected_ids);
    END IF;

    -- Case 1: we have accepted and rejected
    IF accepted_embedding IS NOT NULL AND rejected_embedding IS NOT NULL THEN
        RETURN QUERY
        SELECT 
            t.id::INTEGER,
            abs(l2_distance(t.embedding, accepted_embedding) - l2_distance(t.embedding, rejected_embedding)) AS distance
        FROM all_tags t
        ORDER BY distance ASC;

    -- Case 2: only accepted
    ELSIF accepted_embedding IS NOT NULL THEN
        RETURN QUERY
        SELECT 
            t.id::INTEGER,
            l2_distance(t.embedding, accepted_embedding) AS distance
        FROM all_tags t
        ORDER BY distance ASC;

    -- Case 3: only rejected
    ELSE
        RETURN QUERY
        SELECT 
            t.id::INTEGER,
            l2_distance(t.embedding, rejected_embedding) AS distance
        FROM all_tags t
        ORDER BY distance DESC;  -- further from rejected = better
    END IF;
END;
$$;
