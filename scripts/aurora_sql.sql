-- Prepare Aurora PostgreSQL as a vector store for the Bedrock Knowledge Base.
-- Run in the RDS Query Editor (connect with the stack1 secret, database "myapp"), one statement at a time.

-- 1. pgvector: adds the VECTOR column type and similarity operators
CREATE EXTENSION IF NOT EXISTS vector;

-- 2. A dedicated schema for Bedrock's table
CREATE SCHEMA IF NOT EXISTS bedrock_integration;

-- 3. A database role for Bedrock
DO $$ BEGIN CREATE ROLE bedrock_user LOGIN; EXCEPTION WHEN duplicate_object THEN RAISE NOTICE 'Role already exists'; END $$;
GRANT ALL ON SCHEMA bedrock_integration TO bedrock_user;

-- 4. One row per chunk; vector(1536) matches Titan Text Embeddings V1
CREATE TABLE IF NOT EXISTS bedrock_integration.bedrock_kb (
    id uuid PRIMARY KEY,
    embedding vector(1536),
    chunks text,
    metadata json
);

-- 5. HNSW index on the vectors: fast semantic (nearest-neighbour) search
CREATE INDEX IF NOT EXISTS bedrock_kb_embedding_idx
    ON bedrock_integration.bedrock_kb USING hnsw (embedding vector_cosine_ops);

-- 6. GIN full-text index on the text: required by Bedrock today (enables hybrid / keyword search)
CREATE INDEX IF NOT EXISTS bedrock_kb_chunks_idx
    ON bedrock_integration.bedrock_kb USING gin (to_tsvector('simple', chunks));

-- Checks
-- SELECT * FROM pg_extension;
-- SELECT COUNT(*) FROM bedrock_integration.bedrock_kb;   -- > 0 after the KB sync
