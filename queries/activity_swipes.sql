CREATE OR REPLACE FUNCTION get_matching_activities_by_quiz_tags(input_quiz_id INTEGER, match_count INTEGER)
RETURNS TABLE (id INTEGER, title TEXT, description TEXT, video_uri TEXT, tags TEXT[])
LANGUAGE plpgsql
AS $$
DECLARE
    combined_embedding VECTOR;
    tag_ids INTEGER[];
    schedule_ids INTEGER[];
    essential_ids INTEGER[];
BEGIN
    -- Get tag_ids, schedule_ids, and essential_activities_ids from the quiz
    SELECT 
        string_to_array(trim(both '[]' from q.tags_ids), ',')::INTEGER[],
        string_to_array(trim(both '[]' from q.schedule_ids), ',')::INTEGER[],
        string_to_array(trim(both '[]' from q.essential_activities_ids), ',')::INTEGER[]
    INTO 
        tag_ids,
        schedule_ids,
        essential_ids
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

    -- Return activities ordered by similarity, excluding essential_ids
    RETURN QUERY
    SELECT 
        a.id::INTEGER, 
        a.title::TEXT, 
        a.description::TEXT, 
        a.video_uri::TEXT,
        CASE
            WHEN a.tags IS NULL THEN ARRAY[]::TEXT[]
            ELSE array(SELECT jsonb_array_elements_text(to_jsonb(a.tags)))
        END
    FROM activities a
    WHERE 
        a.schedule_id = ANY(schedule_ids) AND
        (essential_ids IS NULL OR NOT (a.id = ANY(essential_ids)))
    ORDER BY a.embedding <=> combined_embedding
    LIMIT match_count;
END;
$$;
