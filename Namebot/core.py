import aiohttp
import asyncio
from typing import Optional, Dict, Any

async def Namebot(user_id: int, img_unique_id: str, bot_token_link: str, file_id: str) -> Dict[str, Any]:
    """
    Main function to get character name - Direct callable
    
    Args:
        user_id: Telegram user ID
        img_unique_id: Unique image identifier
        bot_token_link: Bot token for verification
        file_id: File ID of the image
        
    Returns:
        Dictionary with character information or error
    """
    # API URL set directly here - Replace with your actual Vercel URL
    api_url = "https://your-namebot-api.vercel.app"
    
    async with aiohttp.ClientSession() as session:
        payload = {
            "user_id": user_id,
            "img_unique_id": img_unique_id,
            "bot_token": bot_token_link,
            "file_id": file_id
        }
        
        try:
            async with session.post(
                f"{api_url}/api/get-character", 
                json=payload,
                headers={"Content-Type": "application/json"}
            ) as response:
                
                if response.status == 200:
                    result = await response.json()
                    return result
                elif response.status == 401:
                    return {
                        "success": False,
                        "error": "Invalid bot token",
                        "message": "Authentication failed"
                    }
                else:
                    try:
                        error_data = await response.json()
                        return {
                            "success": False,
                            "error": error_data.get("error", "Unknown error"),
                            "status_code": response.status
                        }
                    except:
                        return {
                            "success": False,
                            "error": f"HTTP {response.status}",
                            "status_code": response.status
                        }
                        
        except aiohttp.ClientError as e:
            return {
                "success": False,
                "error": f"Connection error: {str(e)}",
                "message": "Failed to connect to API"
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Unexpected error: {str(e)}",
                "message": "An unexpected error occurred"
            }

async def get_character_name(user_id: int, img_unique_id: str, bot_token_link: str, file_id: str) -> Dict[str, Any]:
    """
    Alternative function name for getting character name
    """
    return await Namebot(user_id, img_unique_id, bot_token_link, file_id)

# Health check function (optional)
async def check_api_health() -> Dict[str, Any]:
    """Check if the API is healthy"""
    api_url = "https://your-namebot-api.vercel.app"  # Same URL as above
    
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(f"{api_url}/api/health") as response:
                if response.status == 200:
                    return await response.json()
                else:
                    return {"status": "unhealthy", "code": response.status}
        except Exception as e:
            return {"status": "error", "message": str(e)}
