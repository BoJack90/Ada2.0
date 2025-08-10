-- Script to clean up all generated content from the database
-- This will delete all content while preserving the structure and configurations

-- Start transaction
BEGIN;

-- Delete content variants (actual generated content)
DELETE FROM content_variants;

-- Delete content drafts
DELETE FROM content_drafts;

-- Delete suggested topics
DELETE FROM suggested_topics;

-- Delete content briefs
DELETE FROM content_briefs;

-- Delete correlation rules
DELETE FROM content_correlation_rules;

-- Delete content plans
DELETE FROM content_plans;

-- Reset sequences if using PostgreSQL
-- This will make new IDs start from 1 again
ALTER SEQUENCE IF EXISTS content_variants_id_seq RESTART WITH 1;
ALTER SEQUENCE IF EXISTS content_drafts_id_seq RESTART WITH 1;
ALTER SEQUENCE IF EXISTS suggested_topics_id_seq RESTART WITH 1;
ALTER SEQUENCE IF EXISTS content_briefs_id_seq RESTART WITH 1;
ALTER SEQUENCE IF EXISTS content_correlation_rules_id_seq RESTART WITH 1;
ALTER SEQUENCE IF EXISTS content_plans_id_seq RESTART WITH 1;

-- Commit transaction
COMMIT;

-- Show counts to verify cleanup
SELECT 'content_plans' as table_name, COUNT(*) as count FROM content_plans
UNION ALL
SELECT 'suggested_topics', COUNT(*) FROM suggested_topics
UNION ALL
SELECT 'content_drafts', COUNT(*) FROM content_drafts
UNION ALL
SELECT 'content_variants', COUNT(*) FROM content_variants
UNION ALL
SELECT 'content_briefs', COUNT(*) FROM content_briefs
UNION ALL
SELECT 'content_correlation_rules', COUNT(*) FROM content_correlation_rules;