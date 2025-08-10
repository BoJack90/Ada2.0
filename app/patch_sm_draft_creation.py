#!/usr/bin/env python3
"""Patch to show where to add automatic draft creation for SM topics"""

patch_locations = """
=== PATCH LOCATIONS FOR AUTOMATIC SM DRAFT CREATION ===

1. In app/tasks/main_flow.py - After creating SM topic (around line 863):
   
   db.add(sm_topic)
   db.flush()
   sm_topic_ids.append(sm_topic.id)
   
   # ADD THIS: Create draft for SM topic
   sm_draft = models.ContentDraft(
       suggested_topic_id=sm_topic.id,
       status="pending_generation",
       is_active=True,
       created_at=datetime.utcnow(),
       updated_at=datetime.utcnow()
   )
   db.add(sm_draft)

2. For standalone SM posts (around line 930):
   
   db.add(topic)
   db.flush()
   generated_ids.append(topic.id)
   
   # ADD THIS: Create draft for standalone SM
   standalone_draft = models.ContentDraft(
       suggested_topic_id=topic.id,
       status="pending_generation",
       is_active=True,
       created_at=datetime.utcnow(),
       updated_at=datetime.utcnow()
   )
   db.add(standalone_draft)

3. Alternative: Create a separate function to ensure all SM topics have drafts:

def ensure_sm_topics_have_drafts(db: Session, topic_ids: List[int]):
    '''Ensure all SM topics have associated drafts'''
    for topic_id in topic_ids:
        # Check if draft exists
        existing_draft = db.query(models.ContentDraft).filter(
            models.ContentDraft.suggested_topic_id == topic_id
        ).first()
        
        if not existing_draft:
            draft = models.ContentDraft(
                suggested_topic_id=topic_id,
                status="pending_generation",
                is_active=True,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            db.add(draft)
    
    db.flush()

Then call it after creating SM topics:
ensure_sm_topics_have_drafts(db, sm_topic_ids)
"""

print(patch_locations)

# Create the actual patch file
patch_content = '''--- a/app/tasks/main_flow.py
+++ b/app/tasks/main_flow.py
@@ -862,6 +862,16 @@ def generate_correlated_sm_variants_task(self, plan_id: int):
                         db.add(sm_topic)
                         db.flush()
                         sm_topic_ids.append(sm_topic.id)
+                        
+                        # Create draft for SM topic to ensure visibility in dashboard
+                        sm_draft = models.ContentDraft(
+                            suggested_topic_id=sm_topic.id,
+                            status="pending_generation",
+                            is_active=True,
+                            created_at=datetime.utcnow(),
+                            updated_at=datetime.utcnow()
+                        )
+                        db.add(sm_draft)
                 
                 db.commit()
                 logger.info(f"Created {len(sm_topic_ids)} SM topics for blog topic {topic.id}")
@@ -928,6 +938,16 @@ def generate_correlated_sm_variants_task(self, plan_id: int):
                         db.add(topic)
                         db.flush()
                         generated_ids.append(topic.id)
+                        
+                        # Create draft for standalone SM topic
+                        standalone_draft = models.ContentDraft(
+                            suggested_topic_id=topic.id,
+                            status="pending_generation",
+                            is_active=True,
+                            created_at=datetime.utcnow(),
+                            updated_at=datetime.utcnow()
+                        )
+                        db.add(standalone_draft)
                 
                 db.commit()
                 logger.info(f"Generated {len(generated_ids)} standalone SM posts")
'''

with open('sm_draft_creation.patch', 'w') as f:
    f.write(patch_content)

print("\n✅ Created patch file: sm_draft_creation.patch")
print("Apply with: git apply sm_draft_creation.patch")