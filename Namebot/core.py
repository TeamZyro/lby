import aiohttp
import asyncio
from typing import Optional, Dict, Any, Union
import json

class NameBotAPI:
    """Internal API client for NameBot service"""
    
    def __init__(self, api_url: str = "https://your-app.vercel.app"):
        """
        Initialize the NameBot API client
        
        Args:
            api_url: Base URL of the NameBot API
        """
        self.api_url = api_url.rstrip('/')
        self.session = None
    
    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
    
    async def get_character(self, user_id: int, img_unique_id: str, 
                          bot_token: str, file_id: str) -> Dict[str, Any]:
        """
        Get character name from the API
        
        Args:
            user_id: Telegram user ID
            img_unique_id: Unique identifier for the image
            bot_token: Bot token for authentication
            file_id: Telegram file ID
            
        Returns:
            Dictionary containing the API response
        """
        if not self.session:
            self.session = aiohttp.ClientSession()
        
        payload = {
            "user_id": user_id,
            "img_unique_id": img_unique_id,
            "bot_token": bot_token,
            "file_id": file_id
        }
        
        try:
            async with self.session.post(
                f"{self.api_url}/api/get-character",
                json=payload,
                headers={"Content-Type": "application/json"}
            ) as response:
                
                if response.status == 200:
                    return await response.json()
                else:
                    error_data = await response.json() if response.content_type == 'application/json' else {}
                    return {
                        "success": False,
                        "message": f"API Error: {response.status}",
                        "error": error_data
                    }
                    
        except Exception as e:
            return {
                "success": False,
                "message": f"Request failed: {str(e)}",
                "error": str(e)
            }

class NameBotResult:
    """Result object for NameBot API responses"""
    
    def __init__(self, data: Dict[str, Any]):
        self.raw_data = data
        self.success = data.get("success", False)
        self.character_name = data.get("character_name")
        self.message = data.get("message", "")
        self.source = data.get("source")
        self.error = data.get("error")
    
    def __str__(self):
        if self.success:
            return f"Character: {self.character_name} (Source: {self.source})"
        else:
            return f"Failed: {self.message}"
    
    def __bool__(self):
        return self.success
    
    @property
    def is_success(self) -> bool:
        """Check if the request was successful"""
        return self.success
    
    @property
    def name(self) -> Optional[str]:
        """Get the character name"""
        return self.character_name
    
    @property
    def from_database(self) -> bool:
        """Check if result came from database cache"""
        return self.source == "database"
    
    @property
    def from_api(self) -> bool:
        """Check if result came from external API"""
        return self.source == "api"

# Main API URL - You can change this to your deployed Vercel URL
DEFAULT_API_URL = "https://your-app.vercel.app"  # Replace with your actual URL

async def Namebot(user_id: int, img_unique_id: str, bot_token_link: str, file_id: str, 
                  api_url: str = DEFAULT_API_URL) -> NameBotResult:
    """
    Main function to get character name using NameBot API
    
    Args:
        user_id: Telegram user ID
        img_unique_id: Unique identifier for the image
        bot_token_link: Bot token for authentication
        file_id: Telegram file ID
        api_url: API base URL (optional, uses default if not provided)
    
    Returns:
        NameBotResult object containing the response
    
    Example:
        >>> from zyroname import Namebot
        >>> result = await Namebot(123456, "img_001", "bot_token", "file_123")
        >>> if result.is_success:
        ...     print(f"Character found: {result.name}")
        ... else:
        ...     print(f"Error: {result.message}")
    """
    async with NameBotAPI(api_url) as api:
        response = await api.get_character(user_id, img_unique_id, bot_token_link, file_id)
        return NameBotResult(response)

async def get_character_name(user_id: int, img_unique_id: str, bot_token_link: str, file_id: str,
                           api_url: str = DEFAULT_API_URL) -> Optional[str]:
    """
    Get character name directly (returns only the name string)
    
    Args:
        user_id: Telegram user ID
        img_unique_id: Unique identifier for the image
        bot_token_link: Bot token for authentication
        file_id: Telegram file ID
        api_url: API base URL (optional)
    
    Returns:
        Character name if found, None if not found or error occurred
    
    Example:
        >>> from zyroname import get_character_name
        >>> name = await get_character_name(123456, "img_001", "bot_token", "file_123")
        >>> if name:
        ...     print(f"Character: {name}")
        ... else:
        ...     print("Character not found")
    """
    result = await Namebot(user_id, img_unique_id, bot_token_link, file_id, api_url)
    return result.name if result.is_success else None

# Synchronous wrapper functions for non-async environments
def namebot_sync(user_id: int, img_unique_id: str, bot_token_link: str, file_id: str,
                 api_url: str = DEFAULT_API_URL) -> NameBotResult:
    """
    Synchronous wrapper for Namebot function
    
    Args:
        user_id: Telegram user ID
        img_unique_id: Unique identifier for the image
        bot_token_link: Bot token for authentication
        file_id: Telegram file ID
        api_url: API base URL (optional)
    
    Returns:
        NameBotResult object containing the response
    """
    return asyncio.run(Namebot(user_id, img_unique_id, bot_token_link, file_id, api_url))

def get_character_name_sync(user_id: int, img_unique_id: str, bot_token_link: str, file_id: str,
                           api_url: str = DEFAULT_API_URL) -> Optional[str]:
    """
    Synchronous wrapper for get_character_name function
    
    Args:
        user_id: Telegram user ID
        img_unique_id: Unique identifier for the image
        bot_token_link: Bot token for authentication
        file_id: Telegram file ID
        api_url: API base URL (optional)
    
    Returns:
        Character name if found, None if not found or error occurred
    """
    return asyncio.run(get_character_name(user_id, img_unique_id, bot_token_link, file_id, api_url))
