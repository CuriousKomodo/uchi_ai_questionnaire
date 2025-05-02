import requests
import random
import os


class GifService:
    def __init__(self):
        self.api_key = os.getenv("GIPHY_API_KEY")
        self.fallback_gif = "https://media.giphy.com/media/3o7TKsQ8UQZrJtXXLi/giphy.gif"

    def get_random_gif(self, keyword: str) -> str:
        """Get a random GIF from Giphy based on keyword."""
        if not self.api_key:
            return self.fallback_gif

        url = f"https://api.giphy.com/v1/gifs/search?api_key={self.api_key}&q={keyword}&limit=10"

        try:
            response = requests.get(url)
            data = response.json()
            gifs = data.get("data", [])
            if gifs:
                return random.choice(gifs)["images"]["original"]["url"]
            return self.fallback_gif
        except Exception:
            return self.fallback_gif

    def get_celebration_gif(self) -> str:
        """Get a random celebration GIF."""
        return self.get_random_gif(random.choice(["happy_dancing", "yay"]))

    def get_greeting_gif(self) -> str:
        """Get a random celebration GIF."""
        return self.get_random_gif("hello there")