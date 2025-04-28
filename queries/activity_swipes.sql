CREATE OR REPLACE FUNCTION get_matching_activities_by_quiz_tags(input_quiz_id INTEGER, match_count INTEGER)
RETURNS TABLE (id INTEGER, title TEXT, description TEXT, video_uri TEXT)
LANGUAGE plpgsql
AS $$
DECLARE
    combined_embedding VECTOR;
    tags_string TEXT;
    tag_id_array INTEGER[];
    schedules_string TEXT;
    schedule_id_array INTEGER[];
BEGIN
    -- Get the tags_ids and schedule_ids strings from the quiz
    SELECT q.tags_ids, q.schedule_ids INTO tags_string, schedules_string
    FROM quizzes q
    WHERE q.id = input_quiz_id;
    
    -- Parse the tags string into an array of integers
    SELECT ARRAY(
        SELECT CAST(trim(value) AS INTEGER)
        FROM regexp_split_to_table(
            TRIM(BOTH '[]' FROM tags_string),
            ','
        ) AS value
    ) INTO tag_id_array;
    
    -- Parse the schedules string into an array of integers
    SELECT ARRAY(
        SELECT CAST(trim(value) AS INTEGER)
        FROM regexp_split_to_table(
            TRIM(BOTH '[]' FROM schedules_string),
            ','
        ) AS value
    ) INTO schedule_id_array;
    
    -- Get the combined embedding from tags
    SELECT AVG(t.embedding) INTO combined_embedding
    FROM tags t
    WHERE t.id = ANY(tag_id_array);
    
    -- Return activities ordered by similarity that match schedule_id
    RETURN QUERY
    SELECT 
        CAST(a.id AS INTEGER), 
        a.title, 
        a.description, 
        a.video_uri
    FROM activities a
    WHERE a.schedule_id = ANY(schedule_id_array)
    ORDER BY a.embedding <=> combined_embedding
    LIMIT match_count;
END;
$$;