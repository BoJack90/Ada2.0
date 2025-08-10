#!/bin/bash

# Script to run the database migration for adding indexes

echo "Running database migration to add performance indexes..."

# Change to the project directory
cd /d/Ada2.0 || exit 1

# Run the migration
echo "Applying migration 011_add_content_plans_indexes..."
alembic upgrade head

echo "Migration completed!"
echo ""
echo "Indexes added:"
echo "- content_plans: organization_id, (organization_id, is_active), status, (organization_id, status, is_active)"
echo "- suggested_topics: content_plan_id, (content_plan_id, is_active), (content_plan_id, status, is_active)"
echo "- scheduled_posts: content_plan_id"
echo "- content_briefs: content_plan_id"
echo "- content_correlation_rules: content_plan_id"
echo ""
echo "These indexes will significantly improve query performance for content plan operations."