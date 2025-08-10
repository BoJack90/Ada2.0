-- Fix null meta_data in content_plans
UPDATE content_plans
SET meta_data = '{
    "generation_method": "standard",
    "use_deep_research": false,
    "research_depth": "deep",
    "analyze_competitors": false,
    "include_trends": false,
    "optimize_seo": false
}'::jsonb
WHERE meta_data IS NULL;

-- Verify the fix
SELECT id, plan_period, meta_data 
FROM content_plans 
ORDER BY id DESC;

-- Also ensure meta_data columns in other tables have defaults
UPDATE suggested_topics
SET meta_data = '{}'::jsonb
WHERE meta_data IS NULL;

UPDATE content_variants
SET meta_data = '{}'::jsonb
WHERE meta_data IS NULL;