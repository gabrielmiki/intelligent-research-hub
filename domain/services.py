# "Business Logic" (e.g., Call Google, Parse HTML)
import requests
from bs4 import BeautifulSoup
import os
from google import genai

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

    def summarize_text(self, scraped_text: str) -> str:
        """
        Sends processed text to the Gemini model and returns a formatted markdown summary.
        """
        # 1. Read the API key securely from Docker Secrets
        print("Retrieving API key from Docker secrets...", flush=True)  # Debug statement
        try:
            # api_key = self.get_docker_secret('google_credentials')

            secret_path = f"/run/secrets/google_credentials"
        
            if os.path.exists(secret_path):
                with open(secret_path, "r") as file:
                    # .strip() is crucial to remove invisible newline characters
                    api_key = file.read().strip()
        except Exception as e:
            print(f"Error retrieving API key: {e}", flush=True)
            return f"Error retrieving API key: {str(e)}"

        if not api_key:
            return "Error: Could not locate 'google_credentials' in Docker secrets."

        # 2. Initialize the client
        print("Initializing Google GenAI client...", flush=True)  # Debug statement
        client = genai.Client(api_key=api_key)

        # 3. Craft the Prompt
        prompt = f"""
        You are an expert research assistant. Please read the following text extracted from a webpage and provide a comprehensive, well-structured summary.
        
        Format your response using Markdown:
        - Start with a bold 1-2 sentence TL;DR.
        - Follow with 3-5 bullet points covering the key takeaways.
        - End with a brief conclusion if necessary.
        
        TEXT TO SUMMARIZE:
        {scraped_text}
        """

        try:
            print("Sending prompt to Gemini model...", flush=True)  
            # 4. Call the AI Model (Using gemini-2.5-flash for speed and cost-efficiency)
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=prompt,
            )            
            return response.text
            
        except Exception as e:
            print(f"AI Generation failed: {e}")
            return f"Failed to generate summary due to an API error: {str(e)}"

    def get_docker_secret(self, secret_name: str) -> str:
        """
        Reads a secret from Docker's default secret directory.
        """
        secret_path = f"/run/secrets/{secret_name}"
        
        if os.path.exists(secret_path):
            with open(secret_path, "r") as file:
                # .strip() is crucial to remove invisible newline characters
                return file.read().strip() 
        
        # Fallback for local development if you aren't using swarm/compose secrets locally
        return os.getenv(secret_name.upper())