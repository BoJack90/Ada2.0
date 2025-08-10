#!/usr/bin/env python3
"""
Clean Database Script - Delete all content plans and related data

This script deletes all content-related data from the database to provide
a clean slate for testing. It handles foreign key constraints by deleting
in the correct order.

Tables cleaned:
- ScheduledPost
- ContentVariant  
- ContentDraft
- SuggestedTopic
- ContentBrief
- ContentCorrelationRule
- ContentPlan
"""
import sys
import os
import logging
from datetime import datetime

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from app.db.database import SessionLocal
    from app.db.models import (
        ContentPlan, SuggestedTopic, ContentDraft, ContentVariant, 
        ScheduledPost, ContentBrief, ContentCorrelationRule
    )
except ImportError as e:
    print(f"❌ Failed to import database modules: {e}")
    print("Make sure you're running this script in the correct environment.")
    print("If running in Docker, use: docker-compose exec app python app/delete_all_content_plans.py")
    sys.exit(1)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def get_table_counts(db):
    """Get current count of records in all content tables"""
    return {
        'ContentPlan': db.query(ContentPlan).count(),
        'SuggestedTopic': db.query(SuggestedTopic).count(),
        'ContentDraft': db.query(ContentDraft).count(),
        'ContentVariant': db.query(ContentVariant).count(),
        'ScheduledPost': db.query(ScheduledPost).count(),
        'ContentBrief': db.query(ContentBrief).count(),
        'ContentCorrelationRule': db.query(ContentCorrelationRule).count(),
    }

def print_table_counts(counts, title):
    """Print table counts in a formatted way"""
    print(f"\n=== {title} ===")
    total = sum(counts.values())
    print(f"Total records: {total}")
    print("-" * 40)
    for table, count in counts.items():
        print(f"{table:20}: {count:>6}")

def delete_all_content_data():
    """Delete all content data in the correct order to handle foreign key constraints"""
    db = SessionLocal()
    
    try:
        logger.info("Starting database cleanup process")
        
        # Get initial counts
        initial_counts = get_table_counts(db)
        print_table_counts(initial_counts, "CURRENT DATABASE STATE")
        
        total_initial = sum(initial_counts.values())
        if total_initial == 0:
            print("\n✅ Database is already clean - no records to delete")
            return
        
        # Confirm deletion
        print(f"\n⚠️  WARNING: This will delete ALL {total_initial} content-related records!")
        print("This includes content plans, topics, drafts, variants, and briefs.")
        
        # Auto-confirm for automated environments
        response = "yes"
        print(f"Continue? (yes/no): {response}")
        
        if response.lower() not in ['yes', 'y', 'tak']:
            print("\n❌ Operation cancelled")
            return
        
        print(f"\n🗑️  Starting deletion process at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Delete in correct order to respect foreign key constraints
        deletion_order = [
            (ScheduledPost, "Scheduled Posts"),
            (ContentVariant, "Content Variants"),
            (ContentDraft, "Content Drafts"),
            (SuggestedTopic, "Suggested Topics"),
            (ContentCorrelationRule, "Correlation Rules"),
            (ContentBrief, "Content Briefs"),
            (ContentPlan, "Content Plans"),
        ]
        
        total_deleted = 0
        
        for model, name in deletion_order:
            try:
                count_before = db.query(model).count()
                if count_before > 0:
                    deleted = db.query(model).delete()
                    total_deleted += deleted
                    logger.info(f"Deleted {deleted} records from {name}")
                    print(f"✓ {name}: {deleted} records deleted")
                else:
                    print(f"✓ {name}: No records to delete")
            except Exception as e:
                logger.error(f"Error deleting {name}: {str(e)}")
                raise
        
        # Commit all changes
        db.commit()
        logger.info(f"Successfully deleted {total_deleted} total records")
        
        # Verify deletion
        final_counts = get_table_counts(db)
        print_table_counts(final_counts, "DATABASE STATE AFTER CLEANUP")
        
        remaining_total = sum(final_counts.values())
        if remaining_total == 0:
            print(f"\n✅ CLEANUP COMPLETED SUCCESSFULLY")
            print(f"All {total_deleted} content records have been deleted")
            print("Database is now clean and ready for testing")
        else:
            print(f"\n⚠️  WARNING: {remaining_total} records still remain")
            logger.warning(f"Expected 0 records but {remaining_total} remain")
        
    except Exception as e:
        logger.error(f"Error during cleanup: {str(e)}")
        print(f"\n❌ Error during deletion: {str(e)}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    try:
        delete_all_content_data()
    except KeyboardInterrupt:
        print("\n\n❌ Operation cancelled by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Script failed: {str(e)}")
        print(f"\n❌ Script failed: {str(e)}")
        sys.exit(1)