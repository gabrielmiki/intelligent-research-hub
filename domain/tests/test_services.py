import pytest
from unittest.mock import patch, Mock
from domain.services import ResearchAgent

# 1. Define some "Fake" HTML input to test our cleaning logic
# This includes scripts, styles, and extra whitespace we want to remove.
MOCK_HTML_CONTENT = """
<html>
    <head>
        <title>Test Page</title>
        <style> body { color: red; } </style>
        <script> console.log('bad content'); </script>
    </head>
    <body>
        <nav>Menu 1 | Menu 2</nav>
        
        <h1>   Welcome to the   Article   </h1>
        
        <p>This is the <b>real</b> content.</p>
        
        <footer>Copyright 2024</footer>
    </body>
</html>
"""

# The expected output should NOT have "Menu", "bad content", or "Copyright"
# It should strictly be the H1 and the P text.
EXPECTED_CLEAN_TEXT = "Welcome to the Article This is the real content."

def test_get_content_cleaning_logic():
    """
    Verifies that HTML tags, scripts, and navbars are stripped correctly.
    """
    # PATCH: We intercept 'requests.get' inside the 'domain.services' module
    with patch("domain.services.requests.get") as mock_get:
        
        # Setup the "Fake" Response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = MOCK_HTML_CONTENT
        mock_get.return_value = mock_response

        # Execute
        agent = ResearchAgent()
        result = agent.get_content_from_url("http://fake-url.com")
        
        # Assert
        # 1. Did we actually call the URL?
        mock_get.assert_called_with("http://fake-url.com", headers={'User-Agent': 'Mozilla/5.0'}, timeout=10)
        
        # 2. Did we clean the text?
        assert "console.log" not in result  # Script should be gone
        assert "Menu 1" not in result       # Nav should be gone
        assert "Copyright" not in result    # Footer should be gone
        assert "Welcome to the Article" in result
        
        # Optional: Check if whitespace was normalized
        # (This depends on exactly how strict your cleaning logic is)
        assert "   " not in result 

def test_get_content_network_error():
    """
    Verifies that the code raises an error if the URL is broken.
    """
    with patch("domain.services.requests.get") as mock_get:
        # Setup a fake error (e.g., 404 Not Found)
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.raise_for_status.side_effect = Exception("404 Error")
        mock_get.return_value = mock_response
        
        agent = ResearchAgent()
        
        # We expect this code to crash (raise Exception)
        with pytest.raises(Exception) as excinfo:
            agent.get_content_from_url("http://broken-url.com")
        
        assert "404 Error" in str(excinfo.value)