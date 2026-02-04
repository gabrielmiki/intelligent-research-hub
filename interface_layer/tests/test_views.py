import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from unittest.mock import patch
from django.contrib.auth import get_user_model
from interface_layer.models import Summary

User = get_user_model()

# --- FIXTURES (Setup Code) ---

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def user(db):
    return User.objects.create_user(username="testuser", password="password")

@pytest.fixture
def auth_client(api_client, user):
    """Returns a client that is already logged in."""
    api_client.force_authenticate(user=user)
    return api_client

# --- TESTS ---

@pytest.mark.django_db
def test_create_summary_success(auth_client, user):
    """
    Verifies that a valid POST request:
    1. Returns HTTP 202 Accepted
    2. Creates a DB record
    3. Triggers the Celery task
    """
    url = reverse('submit-summary') # Matches the 'name=' in urls.py
    data = {'url': 'http://valid-url.com'}

    # PATCH: We intercept the Celery task.
    # We don't want to actually start a worker process.
    with patch('interface_layer.views.process_summary_task.delay') as mock_task:
        response = auth_client.post(url, data)

        # 1. Assert Response
        assert response.status_code == status.HTTP_202_ACCEPTED
        assert response.data['status'] == 'PENDING'

        # 2. Assert Database
        assert Summary.objects.count() == 1
        summary = Summary.objects.first()
        assert summary.url == 'http://valid-url.com'
        assert summary.user == user

        # 3. Assert Task was Enqueued
        mock_task.assert_called_once_with(summary.id)

@pytest.mark.django_db
def test_create_summary_invalid_url(auth_client):
    """Verifies valid URL validation."""
    url = reverse('submit-summary')
    data = {'url': 'not-a-url'}

    response = auth_client.post(url, data)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert Summary.objects.count() == 0

@pytest.mark.django_db
def test_get_summary_isolation(auth_client, user):
    """
    Security Test: User A cannot see User B's summaries.
    """
    # 1. Create a summary belonging to a DIFFERENT user
    other_user = User.objects.create_user(username="stranger")
    other_summary = Summary.objects.create(
        user=other_user, 
        url="http://secret.com", 
        status="COMPLETED"
    )

    # 2. Try to access it with our 'auth_client' (User A)
    url = reverse('get-summary-detail', args=[other_summary.id])
    response = auth_client.get(url)

    # 3. Should be 404 Not Found (Not 403 Forbidden - don't leak existence)
    assert response.status_code == status.HTTP_404_NOT_FOUND

@pytest.mark.django_db
def test_list_summaries_filter(auth_client, user):
    """Test the list endpoint and status filtering."""
    # Create 2 summaries for this user
    Summary.objects.create(user=user, url="http://1.com", status="PENDING")
    Summary.objects.create(user=user, url="http://2.com", status="COMPLETED")

    base_url = reverse('list-summaries')

    # Case 1: Get All
    resp_all = auth_client.get(base_url)
    assert len(resp_all.data) == 2

    # Case 2: Filter by COMPLETED
    resp_filtered = auth_client.get(base_url + '?status=COMPLETED')
    assert len(resp_filtered.data) == 1
    assert resp_filtered.data[0]['url'] == 'http://2.com'