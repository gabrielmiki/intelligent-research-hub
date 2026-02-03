import pytest
from django.contrib.auth import get_user_model
from interface_layer.models import Summary

# Use this helper to get your CustomUser model dynamically
User = get_user_model()

@pytest.mark.django_db  # <--- Crucial: Allows the test to create a temporary DB
def test_create_custom_user():
    """
    Test that we can create a user and the custom fields work.
    """
    user = User.objects.create_user(
        username="testuser", 
        password="securepassword123",
        email="testuser@example.com"
    )
    
    assert user.username == "testuser"
    assert user.email == "testuser@example.com"
    assert user.check_password("securepassword123") is True
    assert str(user) == "testuser"

@pytest.mark.django_db
def test_create_summary(db):
    """
    Test that a Summary can be created and linked to a User.
    """
    # 1. Setup: Create a user first (Foreign Key requirement)
    user = User.objects.create_user(username="researcher")
    
    # 2. Action: Create the Summary
    summary = Summary.objects.create(
        user=user,
        url="https://www.example.com/article",
        # We don't set status, relying on the default 'PENDING'
    )
    
    # 3. Assertions
    assert summary.id is not None # UUID should be auto-generated
    assert len(str(summary.id)) > 10 # Just ensuring it looks like a UUID
    assert summary.url == "https://www.example.com/article"
    assert summary.status == "PENDING" # Default value check
    assert summary.user == user # Relationship check
    assert summary.celery_task_id is None # Should be empty initially

@pytest.mark.django_db
def test_user_summary_relationship():
    """
    Test the Reverse Relationship: Can we find summaries starting from the User?
    """
    user = User.objects.create_user(username="boss_user")
    
    # Create 2 summaries for this user
    Summary.objects.create(user=user, url="http://site1.com")
    Summary.objects.create(user=user, url="http://site2.com")
    
    # Check if the 'related_name' works
    assert user.summaries.count() == 2
    assert user.summaries.first().url == "http://site2.com" # Checks ordering (newest first)