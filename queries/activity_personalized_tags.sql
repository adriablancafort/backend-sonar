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
    -- Obtenir vectors d'activitats del qüestionari
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

    -- Calcular embedding mitjà d'activitats acceptades
    IF array_length(accepted_ids, 1) > 0 THEN
        SELECT AVG(a.embedding) INTO accepted_embedding
        FROM activities a
        WHERE a.id = ANY(accepted_ids);
    END IF;

    -- Calcular embedding mitjà d'activitats rebutjades
    IF array_length(rejected_ids, 1) > 0 THEN
        SELECT AVG(a.embedding) INTO rejected_embedding
        FROM activities a
        WHERE a.id = ANY(rejected_ids);
    END IF;

    -- Cas 1: tenim acceptats i rebutjats
    IF accepted_embedding IS NOT NULL AND rejected_embedding IS NOT NULL THEN
        RETURN QUERY
        SELECT 
            t.id::INTEGER,
            abs(l2_distance(t.embedding, accepted_embedding) - l2_distance(t.embedding, rejected_embedding)) AS distance
        FROM all_tags t
        ORDER BY distance ASC;

    -- Cas 2: només acceptats
    ELSIF accepted_embedding IS NOT NULL THEN
        RETURN QUERY
        SELECT 
            t.id::INTEGER,
            l2_distance(t.embedding, accepted_embedding) AS distance
        FROM all_tags t
        ORDER BY distance ASC;

    -- Cas 3: només rebutjats
    ELSE
        RETURN QUERY
        SELECT 
            t.id::INTEGER,
            l2_distance(t.embedding, rejected_embedding) AS distance
        FROM all_tags t
        ORDER BY distance DESC;  -- més lluny dels rebutjats = millor
    END IF;
END;
$$;