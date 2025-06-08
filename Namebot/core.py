import aiohttp
import asyncio
from typing import Optional, Dict, Any

class Namebot:
    def __init__(self, api_url: str = "http://localhost:8000"):
        self.api_url = api_url.rstrip('/')
        
    async def __call__(self, user_id: int, img_unique_id: str, bot_token_link: str, file_id: str) -> Dict[str, Any]:
        """
        Main function to get character name
        
        Args:
            user_id: Telegram user ID
            img_unique_id: Unique image identifier
            bot_token_link: Bot token for verification
            file_id: File ID of the image
            
        Returns:
            Dictionary with character information or error
        """
        async with aiohttp.ClientSession() as session:
            payload = {
                "user_id": user_id,
                "img_unique_id": img_unique_id,
                "bot_token": bot_token_link,
                "file_id": file_id
            }
            
            try:
                async with session.post(f"{self.api_url}/get_character", json=payload) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        error_data = await response.json()
                        return {"error": error_data.get("detail", "Unknown error")}
            except Exception as e:
                return {"error": f"Connection error: {str(e)}"}

# Create default instance
namebot = Namebot()

# Allow both class and function usage
async def get_character_name(user_id: int, img_unique_id: str, bot_token_link: str, file_id: str):
    return await namebot(user_id, img_unique_id, bot_token_link, file_id)
