-- Create RPC function for vector similarity search on BNS chunks
-- Run this in Supabase SQL Editor

CREATE OR REPLACE FUNCTION match_bns_chunks(
  query_embedding vector(1536),
  match_threshold float DEFAULT 0.5,
  match_count int DEFAULT 10,
  filter_chunk_type text DEFAULT NULL
)
RETURNS TABLE (
  section_number varchar,
  chunk_id varchar,
  chunk_type varchar,
  chunk_text text,
  metadata jsonb,
  similarity float
)
LANGUAGE plpgsql
AS $$
BEGIN
  RETURN QUERY
  SELECT
    bns_chunks.section_number,
    bns_chunks.chunk_id,
    bns_chunks.chunk_type,
    bns_chunks.chunk_text,
    bns_chunks.metadata,
    1 - (bns_chunks.embedding <=> query_embedding) AS similarity
  FROM bns_chunks
  WHERE
    (filter_chunk_type IS NULL OR bns_chunks.chunk_type = filter_chunk_type)
    AND 1 - (bns_chunks.embedding <=> query_embedding) > match_threshold
  ORDER BY bns_chunks.embedding <=> query_embedding
  LIMIT match_count;
END;
$$;
