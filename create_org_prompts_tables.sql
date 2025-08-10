-- Create organization-specific AI prompts table
CREATE TABLE IF NOT EXISTS organization_ai_prompts (
    id SERIAL PRIMARY KEY,
    organization_id INTEGER NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    prompt_name VARCHAR(100) NOT NULL,
    prompt_template TEXT NOT NULL,
    base_prompt_id INTEGER REFERENCES ai_prompts(id) ON DELETE SET NULL,
    is_active BOOLEAN NOT NULL DEFAULT true,
    version INTEGER NOT NULL DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    UNIQUE(organization_id, prompt_name)
);

-- Create organization-specific AI model assignments table
CREATE TABLE IF NOT EXISTS organization_ai_model_assignments (
    id SERIAL PRIMARY KEY,
    organization_id INTEGER NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    task_name VARCHAR(100) NOT NULL,
    model_name VARCHAR(100) NOT NULL,
    base_assignment_id INTEGER REFERENCES ai_model_assignments(id) ON DELETE SET NULL,
    is_active BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    UNIQUE(organization_id, task_name)
);

-- Add description columns to base tables if they don't exist
ALTER TABLE ai_prompts ADD COLUMN IF NOT EXISTS description TEXT;
ALTER TABLE ai_model_assignments ADD COLUMN IF NOT EXISTS description TEXT;

-- Create indexes
CREATE INDEX IF NOT EXISTS ix_organization_ai_prompts_organization_id ON organization_ai_prompts(organization_id);
CREATE INDEX IF NOT EXISTS ix_organization_ai_model_assignments_organization_id ON organization_ai_model_assignments(organization_id);