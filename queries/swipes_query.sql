CREATE OR REPLACE FUNCTION swipes_query(input_quiz_id INTEGER, match_count INTEGER)
RETURNS TABLE (id INTEGER, title TEXT, description TEXT, video_uri TEXT, tags TEXT[])
LANGUAGE plpgsql
AS $$
DECLARE
    combined_embedding VECTOR;
    tag_ids INTEGER[];
    schedule_ids INTEGER[];
BEGIN
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
    SELECT AVG(t.embedding) INTO combined_embedding
    FROM tags t
    WHERE t.id = ANY(tag_ids);
    
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
        AND a.video_uri IS NOT NULL 
        AND TRIM(a.video_uri) != '' 
        AND LENGTH(TRIM(a.video_uri)) > 0
    ORDER BY a.embedding <=> combined_embedding
    LIMIT match_count;
END;
$$;
