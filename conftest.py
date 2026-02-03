# conftest.py
import pytest
from rest_framework.test import APIClient
from interface_layer.models import Summary

@pytest.fixture
def api_client():
    """Provides a ready-to-use DRF API Client"""
    return APIClient()

@pytest.fixture
def sample_summary(db):
    """Creates a dummy Summary record in the test DB"""
    return Summary.objects.create(
        url="https://example.com",
        status="PENDING"
    )