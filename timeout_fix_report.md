# API Timeout Issues - Analysis and Solutions

## Problem Summary
Users are experiencing timeout errors (10000ms exceeded) when:
1. Creating a new content plan at the final step
2. Loading the "Plany treści" (Content Plans) view from menu

## Root Causes Identified

### 1. Short API Timeout Configuration
- **Current setting**: 10 seconds (10000ms) in `frontend/src/lib/api.ts`
- **Issue**: This is too short for operations that involve file uploads and complex database operations

### 2. Missing Database Index
- **Table**: `content_plans`
- **Column**: `organization_id` (used in WHERE clauses but not indexed)
- **Impact**: Slow queries when fetching content plans for an organization

### 3. Potential Heavy Operations
- Content plan creation involves multiple steps:
  - File upload processing
  - Database insertions
  - Potential correlation rules creation
  - Status updates

## Recommended Solutions

### 1. Increase API Timeout (Immediate Fix)
Increase the timeout in the API client configuration:

```typescript
// frontend/src/lib/api.ts
export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000, // Increase from 10000 (10s) to 30000 (30s)
  headers: {
    'Content-Type': 'application/json',
  },
})
```

For specific endpoints that might take longer (like content plan creation with file upload):

```typescript
// Add a custom timeout for content plan creation
createWithFile: (data: any, file?: File): Promise<any> => {
  const formData = new FormData()
  
  // Add all data fields to FormData
  Object.keys(data).forEach(key => {
    if (data[key] !== undefined && data[key] !== null) {
      formData.append(key, data[key])
    }
  })
  
  // Add file if provided
  if (file) {
    formData.append('brief_file', file)
  }
  
  return apiClient.post('/api/v1/content-plans', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
    timeout: 60000, // 60 seconds for file uploads
  }).then(res => res.data)
},
```

### 2. Add Database Index (Performance Fix)
Create a migration to add an index on `organization_id` in the `content_plans` table:

```python
# migrations/versions/XXX_add_content_plans_organization_index.py
"""Add index on organization_id in content_plans table

Revision ID: XXX
Revises: previous_revision
Create Date: 2025-01-24
"""
from alembic import op
import sqlalchemy as sa

def upgrade():
    op.create_index(
        'ix_content_plans_organization_id', 
        'content_plans', 
        ['organization_id']
    )
    
    # Also add composite index for common query pattern
    op.create_index(
        'ix_content_plans_org_active', 
        'content_plans', 
        ['organization_id', 'is_active']
    )

def downgrade():
    op.drop_index('ix_content_plans_organization_id', 'content_plans')
    op.drop_index('ix_content_plans_org_active', 'content_plans')
```

### 3. Optimize Content Plan List Query
Add query optimization in the CRUD layer:

```python
# app/db/crud.py
def get_organization_content_plans(self, db: Session, org_id: int) -> List[models.ContentPlan]:
    return db.query(models.ContentPlan).filter(
        models.ContentPlan.organization_id == org_id,
        models.ContentPlan.is_active == True
    ).order_by(models.ContentPlan.created_at.desc()).all()  # Add ordering for consistency
```

### 4. Add Loading States and Progress Indicators
Improve user experience by showing progress during long operations:

```typescript
// In CreatePlanWizard component
const [uploadProgress, setUploadProgress] = useState(0)

// Modify the API call to track progress
const contentPlan = await api.contentPlans.createWithFile(contentPlanData, monthlyBriefFile || undefined, {
  onUploadProgress: (progressEvent) => {
    const percentCompleted = Math.round((progressEvent.loaded * 100) / progressEvent.total)
    setUploadProgress(percentCompleted)
  }
})
```

### 5. Add Request Retry Logic
Implement retry logic for transient failures:

```typescript
// frontend/src/lib/api.ts
import axiosRetry from 'axios-retry'

// Configure retry logic
axiosRetry(apiClient, {
  retries: 3,
  retryDelay: axiosRetry.exponentialDelay,
  retryCondition: (error) => {
    return axiosRetry.isNetworkOrIdempotentRequestError(error) || 
           error.code === 'ECONNABORTED' // Timeout errors
  }
})
```

## Implementation Priority

1. **Immediate (High Priority)**:
   - Increase API timeout to 30 seconds (general) and 60 seconds (file uploads)
   - Add loading states with progress indicators

2. **Short-term (Medium Priority)**:
   - Add database indexes via migration
   - Implement retry logic

3. **Long-term (Low Priority)**:
   - Consider implementing background job processing for heavy operations
   - Add WebSocket support for real-time progress updates

## Testing Recommendations

1. Test content plan creation with various file sizes
2. Monitor query performance after adding indexes
3. Test timeout behavior under different network conditions
4. Verify retry logic doesn't cause duplicate submissions

## Monitoring

Add logging to track:
- API response times
- Database query execution times
- File upload sizes and durations
- Timeout occurrences

This will help identify if further optimizations are needed.