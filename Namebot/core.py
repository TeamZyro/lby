import aiohttp
import asyncio
import base64
import os
from typing import List, Dict, Any, Optional, Union

class Namebot:
    """
    NAMEBOT - A library for identifying anime characters from images.
    
    This library interacts with a character identification API and validates
    user membership in required Telegram channels.
    """
    
    API_URL = "http://cheatbot.twc1.net/getName"
    REQUIRED_CHANNEL = "https://t.me/Zyro_Network"
    
    def __init__(self):
        self._session = None
    
    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create an aiohttp session."""
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession()
        return self._session
    
    async def close(self):
        """Close the aiohttp session."""
        if self._session and not self._session.closed:
            await self._session.close()
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
    
    async def _check_channel_membership(self, user_id: int, bot_token: str) -> bool:
        """
        Check if a user is a member of the required Telegram channel.
        
        Args:
            user_id: Telegram user ID
            bot_token: Telegram bot token for API access
            
        Returns:
            bool: True if user is a member, False otherwise
        """
        session = await self._get_session()
        url = f"https://api.telegram.org/bot{bot_token}/getChatMember"
        
        # Extract channel username from URL
        channel_username = self.REQUIRED_CHANNEL.split("/")[-1]
        
        params = {
            "chat_id": f"@{channel_username}",
            "user_id": user_id
        }
        
        try:
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("ok") and data.get("result", {}).get("status") not in ["left", "kicked"]:
                        return True
                return False
        except Exception as e:
            print(f"Error checking channel membership: {e}")
            return False
    
    async def _download_image(self, file_id: str, bot_token: str) -> Optional[bytes]:
        """
        Download an image from Telegram using file_id.
        
        Args:
            file_id: Telegram file ID
            bot_token: Telegram bot token for API access
            
        Returns:
            bytes: Image data or None if download failed
        """
        session = await self._get_session()
        
        # First, get the file path
        url = f"https://api.telegram.org/bot{bot_token}/getFile"
        params = {"file_id": file_id}
        
        try:
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("ok"):
                        file_path = data["result"]["file_path"]
                        
                        # Now download the file
                        download_url = f"https://api.telegram.org/file/bot{bot_token}/{file_path}"
                        async with session.get(download_url) as file_response:
                            if file_response.status == 200:
                                return await file_response.read()
            return None
        except Exception as e:
            print(f"Error downloading image: {e}")
            return None
    
    async def _query_api(self, image_data: bytes) -> Dict[str, Any]:
        """
        Query the character identification API with image data.
        
        Args:
            image_data: Binary image data
            
        Returns:
            dict: API response
        """
        session = await self._get_session()
        
        # Convert image to base64
        encoded_image = base64.b64encode(image_data).decode('utf-8')
        
        # Prepare payload
        payload = {
            "api_token": "TEST-API-TOKEN",  # Replace with actual token if needed
            "photo_b64": encoded_image
        }
        
        try:
            async with session.post(self.API_URL, json=payload) as response:
                if response.status == 200:
                    return await response.json()
                return {"status": False, "error": f"API returned status code {response.status}"}
        except Exception as e:
            return {"status": False, "error": str(e)}
    
    async def identify(self, user_id: int, image_unique_id: str, bot_token: str, file_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Identify an anime character from an image.
        
        Args:
            user_id: Telegram user ID
            image_unique_id: Unique identifier for the image
            bot_token: Telegram bot token for API access
            file_id: Optional file ID if the image needs to be downloaded
            
        Returns:
            dict: Character information or error message
        """
        # Check if user is a member of the required channel
        is_member = await self._check_channel_membership(user_id, bot_token)
        if not is_member:
            return {
                "status": False,
                "error": "You must join our channel first",
                "join_link": self.REQUIRED_CHANNEL
            }
        
        # Try to get character from MongoDB first (simulated)
        # In a real implementation, this would query MongoDB
        
        # If not found in MongoDB and file_id is provided, download and query API
        if file_id:
            image_data = await self._download_image(file_id, bot_token)
            if image_data:
                result = await self._query_api(image_data)
                return result
            else:
                return {"status": False, "error": "Failed to download image"}
        
        return {"status": False, "error": "Character not found and no file_id provided"}
