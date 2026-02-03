# "Business Logic" (e.g., Call Google, Parse HTML)
import requests

class ResearchAgent:
    def generate_summary(self, url: str) -> str:
        """
        Pure business logic. 
        Input: String
        Output: String
        Does NOT know about the Database.
        """
        # 1. Fetch
        response = requests.get(url)
        raw_text = response.text
        
        # 2. Logic (simulated AI)
        summary = f"Processed {len(raw_text)} chars from {url}"
        
        return summary