# "Business Logic" (e.g., Call Google, Parse HTML)
import requests
from bs4 import BeautifulSoup

class ResearchAgent:
    def get_content_from_url(self, url: str) -> str:
        """
        Fetches the URL and returns CLEAN, human-readable text.
        """
        try:
            # 1. Fetch the raw HTML
            # headers are needed to look like a real browser, otherwise some sites block you
            headers = {'User-Agent': 'Mozilla/5.0'} 
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            # 2. Parse HTML
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 3. THE CLEANING PHASE
            # Remove javascript, css, and structural junk
            for script in soup(["script", "style", "header", "footer", "nav", "aside"]):
                script.extract() # Rips the tag out of the tree

            # 4. Extract Text
            # get_text() joins all text, using a space as separator
            text = soup.get_text(separator=' ')
            
            # 5. Normalize Whitespace
            # "Hello      World" -> "Hello World"
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            clean_text = ' '.join(chunk for chunk in chunks if chunk)
            
            # 6. Truncate (Optional but Recommended)
            # Most LLMs have a limit (e.g., 4000 tokens). 
            # Let's keep the first ~15,000 characters (approx 3000 words)
            return clean_text[:15000]
            
        except Exception as e:
            # In a real app, you might log this error
            print(f"Error scraping {url}: {e}")
            raise e

    def summarize_text(self, text: str) -> str:
        """
        Sends the CLEAN text to the AI Agent.
        """
        # Placeholder for your actual AI call (OpenAI/Gemini/etc)
        return f"Simulated Summary of: {text[:100]}..."