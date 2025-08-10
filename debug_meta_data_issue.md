# Meta Data Debugging Report

## Issue
The `meta_data` field is null in the `content_plans` table despite being properly sent from the frontend.

## Analysis

### 1. Frontend (✅ Working)
The frontend correctly constructs the `meta_data` object in `create-plan-wizard.tsx`:
```typescript
meta_data: {
  generation_method: data.generation_method || 'standard',
  use_deep_research: data.use_deep_research || false,
  research_depth: data.research_depth || 'deep',
  analyze_competitors: data.analyze_competitors || false,
  include_trends: data.include_trends || false,
  optimize_seo: data.optimize_seo || false
}
```

### 2. API Client (✅ Working)
The API client correctly converts `meta_data` to JSON string in `api.ts`:
```typescript
if (key === 'meta_data' && typeof data[key] === 'object') {
  formData.append(key, JSON.stringify(data[key]))
}
```

### 3. API Endpoint (⚠️ Potential Issue)
The API endpoint in `content_plans.py` receives and parses the JSON:
```python
parsed_meta_data = None
if meta_data:
    try:
        parsed_meta_data = json.loads(meta_data)
    except json.JSONDecodeError:
        logger.warning(f"Failed to parse meta_data JSON: {meta_data}")
```

However, there's a potential issue: the `meta_data` Form parameter is defined as `Optional[str] = Form(None)`, which might not be receiving the data correctly.

### 4. Schema Definition (✅ Working)
The schema properly defines `meta_data`:
```python
class ContentPlanBase(BaseModel):
    meta_data: Optional[Dict[str, Any]] = None
```

### 5. CRUD Operations (✅ Working)
The CRUD properly handles `meta_data`:
```python
if plan_data.get('meta_data') is None:
    plan_data['meta_data'] = {}
```

## Root Cause
The issue appears to be in the API endpoint. When using `FormData` with multipart/form-data, the field names might be case-sensitive or there might be an issue with how the form data is being parsed.

## Recommended Fix

### Option 1: Add Debug Logging
Add comprehensive logging to track the data flow:

```python
@router.post("/content-plans", response_model=schemas.ContentPlan, status_code=http_status.HTTP_201_CREATED)
async def create_content_plan(
    # ... other parameters ...
    meta_data: Optional[str] = Form(None),
    # ... other parameters ...
):
    # Add debug logging
    logger.info(f"Received meta_data raw value: {meta_data}")
    logger.info(f"Type of meta_data: {type(meta_data)}")
    
    # Parse meta_data if provided
    parsed_meta_data = None
    if meta_data:
        try:
            parsed_meta_data = json.loads(meta_data)
            logger.info(f"Successfully parsed meta_data: {parsed_meta_data}")
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse meta_data JSON: {meta_data}, error: {e}")
    else:
        logger.warning("No meta_data received in request")
```

### Option 2: Check FormData Field Names
Verify that the field name matches exactly between frontend and backend:

Frontend sends: `formData.append('meta_data', JSON.stringify(data[key]))`
Backend expects: `meta_data: Optional[str] = Form(None)`

### Option 3: Use Request Body Instead of Form Data
Consider using a JSON request body instead of FormData for the non-file fields:

```python
class ContentPlanCreateRequest(BaseModel):
    organization_id: int
    plan_period: str
    blog_posts_quota: int
    sm_posts_quota: int
    correlate_posts: bool
    scheduling_mode: str
    scheduling_preferences: Optional[str] = None
    meta_data: Optional[Dict[str, Any]] = None

@router.post("/content-plans")
async def create_content_plan(
    request: ContentPlanCreateRequest,
    brief_file: Optional[UploadFile] = File(None),
    # ...
):
```

## Immediate Solution
1. Check if the migration `026_fix_null_meta_data_in_content_plans.py` has been run
2. Add debug logging to the API endpoint to see what data is actually being received
3. Verify the exact field names being sent in the FormData

## Testing Steps
1. Create a new content plan with advanced generation options
2. Check the browser's Network tab to see the exact FormData being sent
3. Check the API logs to see what's being received
4. Query the database to see if meta_data is stored