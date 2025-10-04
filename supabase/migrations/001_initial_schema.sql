-- Enable pgvector extension for embeddings
CREATE EXTENSION IF NOT EXISTS vector;

-- BNS sections table
CREATE TABLE bns_sections (
  id SERIAL PRIMARY KEY,
  section_number TEXT UNIQUE NOT NULL,
  title TEXT NOT NULL,

  -- Full text for embeddings
  full_text TEXT NOT NULL,

  -- Hierarchical subsections
  subsections JSONB NOT NULL DEFAULT '[]',

  -- Illustrations and explanations
  illustrations JSONB DEFAULT '[]',
  explanations JSONB DEFAULT '[]',

  -- Metadata
  category TEXT NOT NULL CHECK (category IN ('violence', 'property', 'cyber', 'fraud', 'public_order', 'sexual', 'economic', 'other')),
  severity TEXT NOT NULL CHECK (severity IN ('minor', 'moderate', 'serious', 'very_serious')),
  keywords TEXT[] NOT NULL,
  essential_elements JSONB NOT NULL,

  -- Vector embedding
  embedding vector(1536),

  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Index for vector similarity search
CREATE INDEX bns_sections_embedding_idx ON bns_sections
USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);

-- Regular indexes
CREATE INDEX bns_sections_category_idx ON bns_sections(category);
CREATE INDEX bns_sections_severity_idx ON bns_sections(severity);

-- Predictions log table (audit trail)
CREATE TABLE predictions (
  id SERIAL PRIMARY KEY,
  raw_input TEXT NOT NULL,
  input_language TEXT CHECK (input_language IN ('hindi', 'english', 'hinglish')),
  cleaned_text TEXT,
  extracted_entities JSONB,
  crime_category TEXT,
  crime_severity TEXT,
  predicted_sections JSONB NOT NULL,
  confidence_score FLOAT CHECK (confidence_score >= 0 AND confidence_score <= 1),
  ip_address INET,
  user_agent TEXT,
  processing_time_ms INTEGER,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX predictions_created_at_idx ON predictions(created_at DESC);
CREATE INDEX predictions_ip_address_idx ON predictions(ip_address);

-- Rate limiting table
CREATE TABLE rate_limits (
  ip_address INET PRIMARY KEY,
  request_count INTEGER DEFAULT 0,
  window_start TIMESTAMPTZ DEFAULT NOW(),
  last_request_at TIMESTAMPTZ DEFAULT NOW()
);

-- Function: Vector similarity search
CREATE OR REPLACE FUNCTION match_bns_sections (
  query_embedding vector(1536),
  match_threshold float DEFAULT 0.5,
  match_count int DEFAULT 10
)
RETURNS TABLE (
  id int,
  section_number text,
  title text,
  description text,
  essential_elements jsonb,
  punishment text,
  category text,
  severity text,
  similarity float
)
LANGUAGE plpgsql
AS $$
BEGIN
  RETURN QUERY
  SELECT
    bns_sections.id,
    bns_sections.section_number,
    bns_sections.title,
    bns_sections.description,
    bns_sections.essential_elements,
    bns_sections.punishment,
    bns_sections.category,
    bns_sections.severity,
    1 - (bns_sections.embedding <=> query_embedding) as similarity
  FROM bns_sections
  WHERE 1 - (bns_sections.embedding <=> query_embedding) > match_threshold
  ORDER BY bns_sections.embedding <=> query_embedding
  LIMIT match_count;
END;
$$;

-- Function: Check and update rate limit
CREATE OR REPLACE FUNCTION check_rate_limit(
  client_ip INET,
  max_requests INTEGER DEFAULT 100,
  window_minutes INTEGER DEFAULT 60
)
RETURNS BOOLEAN
LANGUAGE plpgsql
AS $$
DECLARE
  current_count INTEGER;
  window_start TIMESTAMPTZ;
BEGIN
  INSERT INTO rate_limits (ip_address, request_count, window_start)
  VALUES (client_ip, 0, NOW())
  ON CONFLICT (ip_address) DO NOTHING;

  SELECT request_count, rate_limits.window_start
  INTO current_count, window_start
  FROM rate_limits
  WHERE ip_address = client_ip;

  IF window_start < NOW() - (window_minutes || ' minutes')::INTERVAL THEN
    UPDATE rate_limits
    SET request_count = 1,
        window_start = NOW(),
        last_request_at = NOW()
    WHERE ip_address = client_ip;
    RETURN TRUE;
  END IF;

  IF current_count >= max_requests THEN
    RETURN FALSE;
  END IF;

  UPDATE rate_limits
  SET request_count = request_count + 1,
      last_request_at = NOW()
  WHERE ip_address = client_ip;

  RETURN TRUE;
END;
$$;
