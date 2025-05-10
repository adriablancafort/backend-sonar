CREATE OR REPLACE FUNCTION validation_get_matching_activities_by_quiz_tags(input_quiz_id INTEGER, match_count INTEGER)
RETURNS TABLE (id INTEGER, title TEXT, description TEXT, video_uri TEXT, tags TEXT[])
LANGUAGE plpgsql
AS $$
DECLARE
    combined_embedding VECTOR;
    tag_ids INTEGER[];
    schedule_ids INTEGER[];
    is_even BOOLEAN;
BEGIN
    -- Determine if input_quiz_id is even
    is_even := (input_quiz_id % 2 = 0);

    -- Get the tags_ids and schedule_ids directly as arrays from the quiz
    SELECT 
        string_to_array(trim(both '[]' from q.tags_ids), ',')::INTEGER[],
        string_to_array(trim(both '[]' from q.schedule_ids), ',')::INTEGER[]
    INTO 
        tag_ids,
        schedule_ids
    FROM quizzes q
    WHERE q.id = input_quiz_id;
    
    -- Check if quiz exists
    IF tag_ids IS NULL THEN
        RAISE EXCEPTION 'Quiz with ID % not found', input_quiz_id;
    END IF;
    
    -- Get the combined embedding from tags
    IF is_even THEN
        SELECT AVG(t.embedding_personalitzat) INTO combined_embedding
        FROM tags t
        WHERE t.id = ANY(tag_ids);
    ELSE
        SELECT AVG(t.embedding) INTO combined_embedding
        FROM tags t
        WHERE t.id = ANY(tag_ids);
    END IF;
    
    -- Return activities ordered by similarity that match schedule_id
    RETURN QUERY
    SELECT 
        a.id::INTEGER, 
        a.title::TEXT, 
        a.description::TEXT, 
        a.video_uri::TEXT,
        -- Convert JSON array to TEXT[] array
        CASE
            WHEN a.tags IS NULL THEN ARRAY[]::TEXT[]
            ELSE array(SELECT jsonb_array_elements_text(to_jsonb(a.tags)))
        END
    FROM activities a
    WHERE a.schedule_id = ANY(schedule_ids)
    ORDER BY CASE
        WHEN is_even THEN a.embedding_personalitzat <=> combined_embedding
        ELSE a.embedding            <=> combined_embedding
    END
    LIMIT match_count;
END;
$$;
