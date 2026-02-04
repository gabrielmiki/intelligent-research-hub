import pytest
from unittest.mock import patch, MagicMock
from domain.tasks import process_summary_task
from interface_layer.models import Summary
from django.contrib.auth import get_user_model

User = get_user_model()

# This fixture creates a real DB record for us to test with
@pytest.fixture
def pending_summary(db):
    user = User.objects.create_user(username="task_tester")
    return Summary.objects.create(
        user=user,
        url="http://test-task.com",
        status="PENDING"
    )

@pytest.mark.django_db
def test_process_summary_success(pending_summary):
    """
    Test the "Happy Path": Service works -> DB is updated to COMPLETED.
    """
    # PATCH: We mock the entire ResearchAgent class.
    # We don't want to actually scrape or call AI here.
    with patch("domain.tasks.ResearchAgent") as MockAgentClass:
        
        # 1. Setup the Mock Behavior
        mock_agent_instance = MockAgentClass.return_value
        mock_agent_instance.get_content_from_url.return_value = "Cleaned Text Content"
        mock_agent_instance.summarize_text.return_value = "Final AI Summary"
        
        # 2. Run the Task DIRECTLY (Synchronously)
        # We call the function process_summary_task() like a normal python function.
        # We do NOT use .delay() because we want it to run right now in this thread.
        process_summary_task(pending_summary.id)
        
        # 3. Verify the Database was updated
        # We must 'refresh' the object from the DB to see changes
        pending_summary.refresh_from_db()
        
        assert pending_summary.status == "COMPLETED"
        assert pending_summary.input_content == "Cleaned Text Content"
        assert pending_summary.output_summary == "Final AI Summary"
        
        # 4. Verify the Service was called correctly
        mock_agent_instance.get_content_from_url.assert_called_with("http://test-task.com")
        mock_agent_instance.summarize_text.assert_called_with("Cleaned Text Content")

@pytest.mark.django_db
def test_process_summary_failure(pending_summary):
    """
    Test the "Error Path": Service raises error -> DB is updated to FAILED.
    """
    with patch("domain.tasks.ResearchAgent") as MockAgentClass:
        
        # 1. Setup the Mock to CRASH
        mock_agent_instance = MockAgentClass.return_value
        mock_agent_instance.get_content_from_url.side_effect = Exception("Website Down")
        
        # 2. Run the Task
        process_summary_task(pending_summary.id)
        
        # 3. Verify DB captured the failure
        pending_summary.refresh_from_db()
        
        assert pending_summary.status == "FAILED"
        # Optional: You might want to assert that input_content is empty or partial