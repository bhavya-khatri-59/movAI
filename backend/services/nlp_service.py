import os
import json
import threading
import google.generativeai as genai
from config import Config

# Ensure you have GEMINI_API_KEY in your .env
api_key = os.environ.get("GEMINI_API_KEY", getattr(Config, 'GEMINI_API_KEY', None))
if api_key:
    genai.configure(api_key=api_key)

class NLPService:
    def __init__(self):
        # Using a fast, stable alias for the latest flash model
        self.model = genai.GenerativeModel('gemini-flash-latest') if api_key else None

    def _fallback_extract(self, query):
        print("Falling back to local keyword splitting.")
        return [word.lower() for word in query.split() if len(word) > 2]

    def extract_tags_from_query(self, query):
        """
        Uses Gemini to extract core concepts, themes, and genres from a query.
        Falls back to local keyword splitting if API fails or takes > 15s.
        """
        import time
        start_time = time.time()
        if not self.model:
            print("WARNING: No Gemini API key found. Set GEMINI_API_KEY in .env.")
            return self._fallback_extract(query)

        system_prompt = (
            "You are a movie taxonomy expert. The user will provide a natural language description "
            "of a movie they want to watch. Your job is to extract the core themes, genres, moods, "
            "and plot elements into a list of concise tags (1-3 words each).\n"
            "Respond ONLY with a valid JSON array of strings. Do not include formatting or markdown.\n"
            "Example input: 'A dark comedy about time travel and aliens'\n"
            'Example output: ["dark comedy", "time travel", "aliens", "sci-fi", "space", "funny"]\n'
            f"User Query: '{query}'"
        )

        result = {}
        
        def api_call():
            try:
                response = self.model.generate_content(
                    system_prompt,
                    generation_config=genai.GenerationConfig(
                        temperature=0.2,
                    )
                )
                result['text'] = response.text
            except Exception as e:
                result['error'] = str(e)

        # Enforce strict 15 second timeout
        thread = threading.Thread(target=api_call)
        thread.start()
        thread.join(timeout=15.0)

        elapsed = time.time() - start_time

        if thread.is_alive():
            print(f"Gemini API request timed out (>{elapsed:.1f}s). Using fallback.")
            return self._fallback_extract(query)
            
        if 'error' in result:
            print(f"Gemini API Error after {elapsed:.1f}s: {result['error']}")
            return self._fallback_extract(query)
            
        try:
            content = result.get('text', '').strip()
            # Clean up markdown if the LLM accidentally included it
            if content.startswith("```json"):
                content = content[7:-3].strip()
            elif content.startswith("```"):
                content = content[3:-3].strip()
                
            tags = json.loads(content)
            print(f"Gemini success in {elapsed:.1f}s. Extracted: {tags}")
            return [str(t).lower() for t in tags]
            
        except Exception as e:
            print(f"Failed to parse Gemini response: {e}")
            return self._fallback_extract(query)

nlp_service = NLPService()
