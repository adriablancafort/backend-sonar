CREATE OR REPLACE FUNCTION validation_get_tag_distances_by_user_preferences(input_quiz_id INTEGER)
RETURNS TABLE(tag_id INTEGER, distance DOUBLE PRECISION)
LANGUAGE plpgsql
AS $$
DECLARE
    accepted_ids INTEGER[];
    rejected_ids INTEGER[];
    schedule_ids INTEGER[];
    accepted_embedding VECTOR;
    rejected_embedding VECTOR;
    is_even BOOLEAN;
BEGIN
    -- Determine if input_quiz_id is even
    is_even := (input_quiz_id % 2 = 0);

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
        IF is_even THEN
            SELECT AVG(a.embedding_personalitzat) INTO accepted_embedding
            FROM activities a
            WHERE a.id = ANY(accepted_ids);
        ELSE
            SELECT AVG(a.embedding) INTO accepted_embedding
            FROM activities a
            WHERE a.id = ANY(accepted_ids);
        END IF;
    END IF;

    -- Calcular embedding mitjà d'activitats rebutjades
    IF array_length(rejected_ids, 1) > 0 THEN
        IF is_even THEN
            SELECT AVG(a.embedding_personalitzat) INTO rejected_embedding
            FROM activities a
            WHERE a.id = ANY(rejected_ids);
        ELSE
            SELECT AVG(a.embedding) INTO rejected_embedding
            FROM activities a
            WHERE a.id = ANY(rejected_ids);
        END IF;
    END IF;

    -- Cas 1: tenim acceptats i rebutjats
    IF accepted_embedding IS NOT NULL AND rejected_embedding IS NOT NULL THEN
        RETURN QUERY
        SELECT 
            t.id::INTEGER,
            CASE
                WHEN is_even THEN abs(l2_distance(t.embedding_personalitzat, accepted_embedding) - l2_distance(t.embedding_personalitzat, rejected_embedding))
                ELSE         abs(l2_distance(t.embedding, accepted_embedding) - l2_distance(t.embedding, rejected_embedding))
            END AS distance
        FROM all_tags t
        ORDER BY distance ASC;

    -- Cas 2: només acceptats
    ELSIF accepted_embedding IS NOT NULL THEN
        RETURN QUERY
        SELECT 
            t.id::INTEGER,
            CASE
                WHEN is_even THEN l2_distance(t.embedding_personalitzat, accepted_embedding)
                ELSE         l2_distance(t.embedding, accepted_embedding)
            END AS distance
        FROM all_tags t
        ORDER BY distance ASC;

    -- Cas 3: només rebutjats
    ELSE
        RETURN QUERY
        SELECT 
            t.id::INTEGER,
            CASE
                WHEN is_even THEN l2_distance(t.embedding_personalitzat, rejected_embedding)
                ELSE         l2_distance(t.embedding, rejected_embedding)
            END AS distance
        FROM all_tags t
        ORDER BY distance DESC;  -- més lluny dels rebutjats = millor
    END IF;
END;
$$;
